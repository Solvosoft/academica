# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matricula', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='maximum',
            field=models.SmallIntegerField(verbose_name='Maximum number of students', default=0),
            preserve_default=False,
        ),
    ]
