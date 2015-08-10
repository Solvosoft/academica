# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matricula', '0003_auto_20150810_0036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='required_courses',
            field=models.ManyToManyField(related_name='required_courses_rel_+', to='matricula.Course', verbose_name='Required courses', blank=True),
        ),
    ]
