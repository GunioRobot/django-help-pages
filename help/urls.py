from django.conf.urls.defaults import *

urlpatterns = patterns('',

    #list of all categories
    url(r'^$', 'help.views.category_list', name='help_category_list'),

    #individual item - note place in the urlconf to avoid lookup fail
    url(r'^category/(?P<cat_id>.+)/item/(?P<item_id>\d+)/$', 'help.views.single_item', name='help_single_item_by_id'), 
    url(r'^category/(?P<cat_slug>.+)/item/(?P<item_slug>.+)/$', 'help.views.single_item', name='help_single_item_by_slug'), 

    #list of all items in a particular category - works with integer or slug
    url(r'^category/(?P<identifier>.+)/$', 'help.views.item_list', name='help_item_list'),    
)