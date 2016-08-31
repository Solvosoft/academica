from django.apps import AppConfig


class MyAppConfig(AppConfig):

    name = 'matricula.contrib.bills'
    verbose_name = 'bills'

    def ready(self):
        import matricula.contrib.bills.signals