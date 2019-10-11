from django.core.cache import cache

def get_currency(name, klass=None):
    if klass is None:
        from membership_core.models import SystemCurrency as klass
    instance = cache.get(name)
    if instance is None:
        instance = klass.objects.get(currency=name)
        cache.set(name, instance)

    return instance