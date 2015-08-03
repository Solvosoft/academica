# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matricula', '0008_auto_20150802_0152'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='flow',
            field=models.SmallIntegerField(choices=[(0, 'Normal flow (manual enroll activate)'), (1, 'Auto pre-enroll (automatic enroll activate)'), (2, 'Auto enroll (automatic enroll finished)')], verbose_name='Enrollment behavior', default=0),
        ),
    ]
