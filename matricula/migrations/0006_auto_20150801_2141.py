# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matricula', '0005_menuitem'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='menuitem',
            options={'verbose_name_plural': 'Menu Items', 'verbose_name': 'Menu Item'},
        ),
        migrations.RemoveField(
            model_name='menuitem',
            name='is_page',
        ),
        migrations.AddField(
            model_name='menuitem',
            name='publicated',
            field=models.BooleanField(verbose_name='Publicated', default=True),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='order',
            field=models.SmallIntegerField(verbose_name='Menu order'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='parent',
            field=models.ForeignKey(verbose_name='Page parent', to='matricula.MenuItem', null=True),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='require_authentication',
            field=models.BooleanField(verbose_name='Authentication is required', default=False),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='type',
            field=models.SmallIntegerField(default=0, verbose_name='Type', choices=[(0, 'Internal'), (1, 'Page')]),
        ),
    ]
