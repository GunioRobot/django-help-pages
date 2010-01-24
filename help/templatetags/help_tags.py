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

    print search_form
    return  { 
                'search_form':search_form,
            }