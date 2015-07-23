# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Colon_Exchange',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_dolar', models.DecimalField(verbose_name='Amount', decimal_places=2, max_digits=6)),
            ],
        ),
        migrations.AddField(
            model_name='bill',
            name='currency',
            field=models.CharField(verbose_name='Currency', max_length=3, default='CRC'),
        ),
        migrations.AlterField(
            model_name='bill',
            name='amount',
            field=models.DecimalField(verbose_name='Amount', decimal_places=2, max_digits=10),
        ),
    ]
