#help.models

import re

from django.db import models
from django.contrib.auth.models import User

from tagging.fields import TagField
from tagging.models import Tag

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
            query = None
            qs = self.get_query_set() 

            search_terms = unescape(search_terms)
            query = search_terms.lower()
            query = re.sub(r'\W+', ' ', query)    #strip non-alphanumerics from string
            tokens = query.split()

            for t in tokens:
                # iteratively build a chain of filter()s that narrow down the search selection
                # to contain all words that are or start with every one of the tokens entered 
                qs = qs.filter(denormed_search_terms__contains = " %s" % t)
            
            return qs

        except Exception, e:
            logging.error("%s when searching for %s -- %s" % (type(e), search_terms, e) )
            return self.model.objects.none()


class HelpItem(HelpBase):
    """
    Holds the actual help item info
    """
    category  = models.ForeignKey('HelpCategory')
    heading   = models.CharField(blank=False, max_length=255, help_text='No HTML in the this label, please')
    body      = models.TextField(blank=False, help_text="Main content for the Help item")

    #add another manager, to help with search, plus a denormed search content column to speed things up
    search_manager    = HelpItemSearchManager()
    denormed_search_terms = models.TextField(editable=False, blank=True, null=True)

    help_tags = TagField("Tags", help_text="Optional tags that will help this item be shown on other pages. Put spaces between tags. Avoid all punctuation. If a tag is multiple words, enclose it in quote marks. Consult the official list of which tags the system is expecting to associated with which pages. Cheers!")

    class Meta:
        verbose_name=("Help item")
        verbose_name_plural=("Help item")
        
    def _get_tags(self):
        return Tag.objects.get_for_object(self)

    def _set_tags(self, tag_list):
        Tag.objects.update_tags(self, tag_list)

    tags = property(_get_tags, _set_tags)    


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

