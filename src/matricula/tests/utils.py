from django.contrib.auth.models import User


def login_report_admin(client):
    """Inicia sesión con un superusuario: las APIs de reportes requieren permisos."""
    user, _created = User.objects.get_or_create(
        username='report_admin',
        defaults={'is_superuser': True, 'is_staff': True, 'email': 'report_admin@example.com'})
    client.force_login(user)
    return user
