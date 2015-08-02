# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from matricula.menues import main_menu


def add_menu(apps, schema_editor):
    MenuItem = apps.get_model("matricula", "MenuItem")
    db_alias = schema_editor.connection.alias
    menues = []
    for menu in main_menu:
        menues.append(MenuItem(
                name=menu[1],
                type=0,
                description=menu[0],
                require_authentication=menu[2],
                is_page=False,
                order=menu[3]) 
                )
    MenuItem.objects.using(db_alias).bulk_create(menues)

class Migration(migrations.Migration):

    dependencies = [
        ('matricula', '0004_auto_20150722_2308'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(verbose_name='Name', max_length=50)),
                ('type', models.SmallIntegerField(default=0, choices=[(0, 'Internal'), (1, 'External')], verbose_name='Type')),
                ('description', models.CharField(verbose_name='Description', max_length=50)),
                ('require_authentication', models.BooleanField(default=False)),
                ('is_page', models.BooleanField(default=False)),
                ('order', models.SmallIntegerField()),
                ('parent', models.ForeignKey(null=True, to='matricula.MenuItem')),
            ],
        ),
        migrations.RunPython(
            add_menu,
        ),
    ]
