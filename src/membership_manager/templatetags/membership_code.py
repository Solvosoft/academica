from django import template
register = template.Library()


@register.simple_tag
def url_replace(request, field, value):
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()


@register.filter(name='index_str')
def index_str(array, index):
    int_index = 2
    if index == "active":
        int_index = 0
    elif index == "inactive":
        int_index = 1
    dev = array[int_index]
    return dev

@register.filter(name='index')
def index(array, index):
    dev = array[index]
    return dev
