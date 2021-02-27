from django.contrib import admin
from membership_core.models import SystemCurrency, Country


admin.site.register([SystemCurrency, Country])
