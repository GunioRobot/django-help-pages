#help.models
from django.db import models

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
    objects = models.Manager()
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
        subcats = list(self.helpcategory_set.all())

        for s in subcats:
            cats = s.helpcategory_set.all()
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


class HelpItem(HelpBase):
    """
    Holds the actual help item info
    """
    category  = models.ForeignKey('HelpCategory')
    heading   = models.CharField(blank=False, max_length=255, help_text='No HTML in the this label, please')
    body      = models.TextField(blank=False, help_text="Main content for the Help item")

    def __unicode__(self):
         return u"%s: '%s' " % (self.category.title, self.heading)

    class Meta:
        verbose_name=("Help item")
        verbose_name_plural=("Help item")
        
    @property
    def related_items(self):
        "Returns a list of items in the same category as before"
        
        
