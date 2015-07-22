# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matricula', '0002_group_is_open'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enroll',
            name='bill_created',
            field=models.BooleanField(default=False, verbose_name='Bill created'),
        ),
    ]
