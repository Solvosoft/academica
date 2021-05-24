from djgentelella.groute import register_lookups
from djgentelella.views.select2autocomplete import BaseSelect2View
from .models import Category


@register_lookups(prefix="category", basename="categorybasename")
class CategoryGModelLookup(BaseSelect2View):
    model = Category
    fields = ['name']
