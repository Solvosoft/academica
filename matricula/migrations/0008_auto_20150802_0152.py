# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matricula', '0007_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='is_index',
            field=models.BooleanField(verbose_name='Index page', default=False),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='parent',
            field=models.ForeignKey(blank=True, to='matricula.MenuItem', null=True, verbose_name='Page parent'),
        ),
    ]
