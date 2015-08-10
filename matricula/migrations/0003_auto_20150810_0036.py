# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matricula', '0002_auto_20150808_2114'),
    ]

    operations = [
        migrations.RenameField(
            model_name='classroomgroupprofesor',
            old_name='Classroom',
            new_name='classroom',
        ),
    ]
