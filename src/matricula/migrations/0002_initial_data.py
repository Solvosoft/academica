from django.db import migrations

from matricula.menues import main_menu
from matricula.utils import load_email_templates


def load_menu(apps, schema_editor):
    MenuItem = apps.get_model('matricula', 'MenuItem')
    for description, name, require_authentication, order, _use_reverse in main_menu:
        MenuItem.objects.get_or_create(
            name=name, defaults={
                'type': 0,
                'description': str(description),
                'require_authentication': require_authentication,
                'order': order,
            })


def load_templates(apps, schema_editor):
    load_email_templates(apps.get_model('async_notification', 'EmailTemplate'))


class Migration(migrations.Migration):

    dependencies = [
        ('matricula', '0001_initial'),
        ('async_notification', '0008_normalize_compliance_emails'),
    ]

    operations = [
        migrations.RunPython(load_menu, migrations.RunPython.noop),
        migrations.RunPython(load_templates, migrations.RunPython.noop),
    ]
