from django.apps import AppConfig


class MatriculaConfig(AppConfig):
    name = 'matricula'
    verbose_name = 'Matrícula'

    def ready(self):
        from matricula.utils import register_email_contexts
        register_email_contexts()
