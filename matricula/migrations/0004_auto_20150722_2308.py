# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matricula', '0003_auto_20150722_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='currency',
            field=models.CharField(choices=[('USD', 'US Dollar'), ('EUR', 'Euro'), ('CRC', 'Costa Rican Colon')], verbose_name='Currency', default='CRC', max_length=3),
        ),
        migrations.AlterField(
            model_name='group',
            name='cost',
            field=models.DecimalField(verbose_name='Course cost', decimal_places=2, max_digits=10),
        ),
    ]
