# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0002_auto_20150722_2359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='colon_exchange',
            name='is_dolar',
            field=models.DecimalField(decimal_places=4, max_digits=6, verbose_name='Amount'),
        ),
    ]
