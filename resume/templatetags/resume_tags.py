from django import template

register = template.Library()

@register.filter
def plural_years(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''

    if value % 10 == 1 and value % 100 != 11:
        return f"{value} рік"
    elif 2 <= value % 10 <= 4 and not (12 <= value % 100 <= 14):
        return f"{value} роки"
    else:
        return f"{value} років"
