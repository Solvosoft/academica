from django.apps import AppConfig


class MembershipManagerConfig(AppConfig):
    name = 'membership_manager'
    verbose_name = "Gestión de membresías"

    def ready(self):
        import membership_manager.signals
