from datetime import timedelta

from django.utils import timezone


def get_dates(filt):
    max_date = timezone.now() + timedelta(days=int(filt))
    min_date = max_date - timedelta(days=1)
    return min_date,max_date

