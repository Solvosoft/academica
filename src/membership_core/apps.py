from django.apps import AppConfig


class MembershipCoreConfig(AppConfig):
    name = 'membership_core'
    verbose_name = "Base para membresias"

    def ready(self):
        import  membership_core.signals