from django import template

register = template.Library()

@register.filter(name='get_id')
def get_id(dictionary):
    """Obtiene el campo _id de un diccionario de MongoDB evitando la restricción del guion bajo."""
    if isinstance(dictionary, dict):
        return str(dictionary.get('_id', ''))
    return ''
