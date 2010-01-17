#views for help app 
from django.conf import settings

from django.http import Http404
from django.shortcuts import get_object_or_404

from help.shortcuts import render_with_context
from help.models import HelpCategory, HelpItem

def category_list(request, template='help_category_list.html'):
    
    tree = None

    top_categories = HelpCategory.objects.filter(parent=None)
    
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
        except HelpCategoryDoesNotExist:
            raise Http404

    help_items = HelpItem.published_objects.filter(category=category)
    print help_items
    
    trail = category.trail
    
    return render_with_context(request, template, {'category':category, 'help_items':help_items, 'trail':trail } )
    
    
def single_item(request, cat_id=None, cat_slug=None, item_id=None, item_slug=None, template='help_single_item.html'):
    """
    Individual help item view 
    """

    help_item = get_object_or_404(HelpItem, id=item_id)

    return render_with_context(request, template, {'item':help_item } )