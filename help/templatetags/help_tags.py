from django import template
register = template.Library()

from help.forms import SearchForm

@register.inclusion_tag('includes/help_search_form.html')
def help_search_form(query=None):

    """ 
    Quick inclusion tag to spit out a search input for the help 
    section. 

    It takes an optional 'query' argument, which enables you to 
    pass in the just-requested search query so that the form 
    has it pre-set if you wish. For example, if your template's 
    context includes the most recent  search query as the 
    variable 'query', just use this in your template:
    
    {% help_search_form query %}
    
    to ensure the search box contains the terms that were just 
    searched for. This is optional, of course, and solely
    
    {% help_search_form %}

    will render the (empty) form too. 
    
    Feel free to ignore this entire tag if you prefer - it's 
    just a nicety.

    """

    kwargs = {}
    
    if query:
        kwargs['query'] = query
    
    search_form = SearchForm(kwargs)

    return  { 
                'search_form':search_form,
            }
            



@register.inclusion_tag('includes/help_usefulness_rating.html')
def help_usefulness_rating(item, request):

    """ 
    Inclusion tag to handle authenticated and (TODO) unauthenticated
    users marking items as useful

    Takes two arguments, the helpitem in question and also the request

    """    
    #look up to see if the user has rated this HelpItem
    found_useful = request.user in item.users_who_found_this_useful.all()
    if not found_useful:
        found_not_useful = request.user in items.users_who_found_this_not_useful.all()
        
    usefulness_score = ("%s/%s") % item.get_usefulness_score()
    
    return {
                'item':item,
                'found_useful':found_useful,
                'found_not_useful':found_not_useful,
                'usefulness_score':usefulness_score
            }
