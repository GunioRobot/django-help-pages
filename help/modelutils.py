"""
Handy utils gathered from the web
"""

import re, htmlentitydefs

def unescape(text):
    """
    Hat-tip to http://effbot.org/zone/re-sub.htm#unescape-html        
    """
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)
    


    
def update_specific_fields(instance, **kwargs):
    """                                                                         
    Update selected model fields in the database, but leave the other           
    fields alone. Use this rather than model.save() for performance             
    and data consistency.                                                       
    Based on: http://www.djangosnippets.org/snippets/479/
    """
    try:
        sql = ['UPDATE', connection.ops.quote_name(instance._meta.db_table), 'SET']
        values = []
        for field_name in kwargs:
            try:
                setattr(instance, field_name, kwargs[field_name])
                field = instance._meta.get_field(field_name)
                value = field.get_db_prep_save(kwargs[field_name])
                if isinstance(value, models.Model):
                    value = value.id
                sql.extend((connection.ops.quote_name(field.column), '=', '%s', ','))
                values.append(value)
            except FieldDoesNotExist, e:
                pass
        sql.pop(-1) # Remove the last comma                                         
        sql.extend(['WHERE', 'id', '=', '%s'])
        values.append(instance.id)
        sql = ' '.join(sql)
        connection.cursor().execute(sql, values)
        transaction.commit_unless_managed()
        return True
    except Exception, e:
        return False
update_specific_fields.alters_data = True
