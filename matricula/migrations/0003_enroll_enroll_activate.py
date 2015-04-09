# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matricula', '0002_auto_20150407_2204'),
    ]

    operations = [
        migrations.AddField(
            model_name='enroll',
            name='enroll_activate',
            field=models.BooleanField(default=False),
        ),
    ]
