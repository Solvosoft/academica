# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_description', models.CharField(max_length=300, verbose_name='Short description')),
                ('description', models.TextField(verbose_name='Description')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Amount')),
                ('currency', models.CharField(max_length=3, default='CRC', verbose_name='Currency')),
                ('is_paid', models.BooleanField(default=False)),
                ('paid_date', models.DateTimeField(auto_now_add=True)),
                ('transaction_id', models.TextField(blank=True, null=True, max_length=300)),
            ],
            options={
                'verbose_name_plural': 'Bills',
                'verbose_name': 'Bill',
            },
        ),
        migrations.CreateModel(
            name='Colon_Exchange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_dolar', models.DecimalField(decimal_places=4, max_digits=10, verbose_name='Amount')),
            ],
        ),
    ]
