
from ajax_select import register, LookupChannel
from django.db.models import Q

from membership_manager.models import Organization, Contact


@register('orgs')
class OrgsLookup(LookupChannel):

    model = Organization

    def get_query(self, q, request):

        return self.model.objects.filter(name__icontains=q)

    def format_item_display(self, item):
        return u"<span class='tag'>%s</span>" % item.name

@register('contacts')
class ContactsLookup(LookupChannel):

    model = Contact

    def get_query(self, q, request):

        return self.model.objects.filter(Q(first_name__icontains=q)|Q(
            last_name__icontains=q )|Q(email__icontains=q ))

    def format_item_display(self, item):
        return u"<span class='tag'>%s</span>" % str(item)

