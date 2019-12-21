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
admin.site.site_title = "Membresias de Código Sur"
admin.site.site_header = "Membresias de Código Sur"
admin.site.index_title = "Membresias de Código Sur"
admin.site.index_template =  'admin/dashboard/welcome.html'

