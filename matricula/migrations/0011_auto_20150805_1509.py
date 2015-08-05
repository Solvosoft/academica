# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matricula', '0010_auto_20150804_0045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menutranslations',
            name='name',
            field=models.CharField(verbose_name='Description', max_length=50),
        ),
    ]
