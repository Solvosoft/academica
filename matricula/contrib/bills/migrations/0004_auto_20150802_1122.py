# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0003_auto_20150802_1120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='colon_exchange',
            name='is_dolar',
            field=models.DecimalField(decimal_places=4, verbose_name='Amount', max_digits=10),
        ),
    ]
