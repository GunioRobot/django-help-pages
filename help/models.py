#help.models

import re

from django.db import models

from django.contrib.auth.models import User

from help.modelutils import unescape, update_specific_fields


class PublishedObjectsManager(models.Manager):
    """
    Auto-filters-out disabled/unpublished messages 
    """
    def get_query_set(self):
        return super(PublishedObjectsManager, self).get_query_set().exclude(published=False)
        

class HelpBase(models.Model):
    """Abstract base model for Help models"""

    slug      = models.SlugField(help_text="Automatically generated; editable, but do so with caution as it changes URLs")
    published = models.BooleanField("Live on site?",  default=True) 
    order     = models.FloatField(default="1.0", 
                help_text='Lists will run from smaller numbers at top to bigger at bottom. Decimal points are allowed for fine control')

    #retain original manager, and add enabled-filtering one
    objects   = models.Manager()
    published_objects = PublishedObjectsManager() #custom manager to make life easier

    class Meta:
        abstract = True
        ordering = ['order']


class HelpCategory(HelpBase):
    """
    Main node for a topic area or sub-topic area 
    """
    parent    = models.ForeignKey('HelpCategory', null=True, blank=True)
    title     = models.CharField(blank=False, max_length=255, help_text='No HTML in the this label, please')

    class Meta:
        verbose_name=("Help category")
        verbose_name_plural=("Help categories")

    def __unicode__(self):
        return u"%s" % (self.title)

    @property
    def subcategories(self):
        """Returns a recursively generated list of any subcategories for the category"""

        children = []
        subcats = list(self.helpcategory_set.all().order_by('order'))

        for s in subcats:
            cats = s.helpcategory_set.all().order_by('order')
            if len(cats) > 0:
                children.append([s, s.subcategories])
            else:
                children.append([s])
        return children
        
    @property
    def trail(self):
        trail = []
        parent = self.parent
        trail.append(self)
        while parent is not None:
            trail.append(parent)
            parent = parent.parent 
        
        return trail[::-1]


class HelpItemSearchManager(PublishedObjectsManager):
    """
    Quick manager class to assist with search - extends PublishedObjectsManager 
    so that it only searches published objects 
    """

    def search(self, search_terms):
        try:
            search_terms = search_terms[:64] #limit to 64 chars
            print search_terms
            query = None
            qs = self.get_query_set() 

            search_terms = unescape(search_terms)
            query = search_terms.lower()
            query = re.sub(r'\W+', ' ', query)    #strip non-alphanumerics from string
            tokens = query.split()
            print 'tokens',tokens

            for t in tokens:
                # iteratively build a chain of filter()s that narrow down the search selection
                # to contain all words that are or start with every one of the tokens entered 
                qs = qs.filter(denormed_search_terms__contains = " %s" % t)
                
            return qs

        except Exception, e:
            print e
            #insert your logging call here
            
            return self.model.objects.none()


class HelpItem(HelpBase):
    """
    Holds the actual help item info
    """
    category  = models.ForeignKey('HelpCategory')
    heading   = models.CharField(blank=False, max_length=255, help_text='No HTML in the this label, please')
    body      = models.TextField(blank=False, help_text="Main content for the Help item")

    users_who_found_this_useful = models.ManyToManyField(User, related_name="user_found_helpful")
    users_who_found_this_not_useful = models.ManyToManyField(User, related_name="user_found_not_helpful")
    
    total_useful_votes      = models.IntegerField(blank=True, null=True, default=0)
    total_not_useful_votes  = models.IntegerField(blank=True, null=True, default=0)

    #add another manager, to help with search, plus a denormed search content column to speed things up
    search_manager    = HelpItemSearchManager()
    denormed_search_terms = models.TextField(editable=False, blank=True, null=True)

    class Meta:
        verbose_name=("Help item")
        verbose_name_plural=("Help item")
        
    def save(self):
        """
        Overriding save() to denorm the search content - we could 
        use Full Text Searching instead, but that's not DB-independent.
        
        Includes category.title to improve hit usefulness
        """
        self.denormed_search_terms = self.heading.lower() + " " + self.body.lower() + " " + self.category.title.lower()
        super(HelpItem, self).save()
        
    def __unicode__(self):
         return u"%s: '%s' " % (self.category.title, self.heading)

    @property
    def related_items(self):
        "Returns a list of items in the same category as before"
        related = self.parent.helpitem_set.exclude(id=self.id)
        return related

    def found_useful_by(user):
        "Convenience method for associating a known user's liking of this item"
        if user.is_authenticated:
            self.users_who_found_this_useful.add(user)
            # and update the specific denormed field ONLY - ie, don't use save()
            attrs = {'total_useful_votes': self.total_useful_votes + 1}            
            update_specific_fields(self, **attrs)

    def found_not_useful_by(user):
        "Convenience method for associating a known user's liking of this item"
        if user.is_authenticated:
            self.users_who_found_this_not_useful.add(user)
            # and update the specific denormed field ONLY - ie, don't use save()
            attrs = {'total_not_useful_votes': self.total_not_useful_votes + 1}            
            update_specific_fields(self, **attrs)
        
    def reset_usefulness_for_user(user):
        "Convenience resetting method."
        if user.is_authenticated:
            if user in self.users_who_found_this_useful:
                self.users_who_found_this_useful.delete(user)
                # and update the specific denormed field ONLY - ie, don't use save()
                attrs = {'total_useful_votes': self.total_useful_votes - 1}            
                update_specific_fields(self, **attrs)
            elif user in self.users_who_found_not_this_useful:
                self.users_who_found_this_not_useful.delete(user)
                # and update the specific denormed field ONLY - ie, don't use save()
                attrs = {'total_not_useful_votes': self.total_not_useful_votes - 1}            
                update_specific_fields(self, **attrs)

    def get_usefulness_score():
        "Returns tuple containing number of votes for it being useful and total number of votes"
        return (self.total_useful_votes, self.total_useful_votes + self.total_not_useful_votes)

