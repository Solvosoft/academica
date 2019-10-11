from django.db.models.signals import post_save

from django.dispatch import receiver
from membership_core.models import SystemCurrency
from django.core.cache import cache

@receiver(post_save, sender=SystemCurrency)
def my_handler(sender, **kwargs):
    instance = kwargs['instance']
    cache.delete(instance.currency)
