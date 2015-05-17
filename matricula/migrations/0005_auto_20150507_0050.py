# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('matricula', '0004_auto_20150507_0000'),
    ]

    operations = [
        migrations.AddField(
            model_name='bill',
            name='is_paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='bill',
            name='paid_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 7, 6, 50, 13, 13797, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
