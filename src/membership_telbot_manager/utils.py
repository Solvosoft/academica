from membership_telbot_manager.models import TelGroup

def get_telegram_group(membership):
    if membership.organization:
        return TelGroup.objects.filter(organization_id=membership.organization.pk).first()

