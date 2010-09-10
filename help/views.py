#views for help app 
from django.conf import settings

import urllib

from django.http import Http404
from django.shortcuts import get_object_or_404

from help.shortcuts import render_with_context
from help.models import HelpCategory, HelpItem
from help.forms import SearchForm

def category_list(request, template='help_category_list.html'):
    
    tree = None

    top_categories = HelpCategory.objects.filter(parent=None).order_by('order')
    
    branches = []

    for top_category in top_categories:
        subcategories = top_category.subcategories
        if len(subcategories) == 0:
            branches.append([top_category])
        else:
            branches.append([top_category, subcategories])
            
    return render_with_context(request, template, {'branches':branches})
    




def item_list(request, identifier=None, template="help_item_list.html"):
    """
    Lists all the items in that category
    """
    try:
        category = HelpCategory.published_objects.get(id=identifier)
    except (HelpCategory.DoesNotExist, ValueError): #ValueError would be trying to pass a string as an int
        try:
            category = HelpCategory.published_objects.get(slug=identifier)
        except HelpCategory.DoesNotExist:
            raise Http404

    help_items = HelpItem.published_objects.filter(category=category).order_by('order')
    
    trail = category.trail
    
    return render_with_context(request, template, {'category':category, 'help_items':help_items, 'trail':trail } )
    
    
    
def items_by_tag(request, tag, template="help_items_by_tag.html"):
    """
    Lists all the items that are tagged with the relevant category
    """

    #convert tag back to unurlencoded
    fixed_tag = urllib.unquote(tag)

    return render_with_context(request, template, {'tag':fixed_tag} )
    
    
    
def single_item(request, cat_identifier, item_identifier, template='help_single_item.html'):
    """
    Individual help item view 
    """
    #see if we can make the identifiers into ints, so we know they'll be pks
    try:
        cat_identifier = int(cat_identifier)
    except:
        pass

    #ditto item_identifiers
    try:
        item_identifier = int(item_identifier)
    except:
        pass    
    try:
        #if we're talking ints, we can go straight for it
        if isinstance(item_identifier, int):
            help_item = get_object_or_404(HelpItem, id=item_identifier)
        else:
            #else if we're talking slugs so can't rely on unique ones
            qs = HelpItem.published_objects
        
            #filter the category first
            if isinstance(cat_identifier, int):
                qs = qs.filter(category=cat_identifier)
            else:
                qs = qs.filter(category__slug=cat_identifier)
        
            #then try to get the item, which has a slug as an identifier
            help_item = qs.get(slug=item_identifier)
        
    except (HelpItem.DoesNotExist): #ValueError would be trying to pass a string as an int
        raise Http404
            
            
    return render_with_context(request, template, {'item':help_item } )
    
    
    
    
    
def search_results(request, template="search_results.html"):
    """
    Displays relevant help items based on the search query entered
    
    Query is sent as a GET, and uses the very simple form help.forms.SearchForm 
    """
    
    query = request.GET.get('query', None)
    
    hits = HelpItem.search_manager.search(query)    
                
    return render_with_context(request, template, {'query':query, 'hits':hits } )
    
    
    