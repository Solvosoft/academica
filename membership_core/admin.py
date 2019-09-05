from django.contrib import admin
from membership_core import models

# Register your models here.
admin.site.register([
    models.SystemCurrency, models.Service, models.RenewalPeriod,

])

class MembershipTemplateAdmin(admin.ModelAdmin):
    list_filter = ('state',  'services')
    search_fields = ('name', 'currency')
    list_display = ('name', 'annual_cost', 'currency', 'renewal_period', 'state')
    filter_horizontal = ['services']


admin.site.register(models.MembershipTemplate, MembershipTemplateAdmin)

