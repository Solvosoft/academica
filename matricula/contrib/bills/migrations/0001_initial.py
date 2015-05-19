# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('short_description', models.CharField(verbose_name='Short description', max_length=300)),
                ('description', models.TextField(verbose_name='Description')),
                ('amount', models.DecimalField(verbose_name='Amount', max_digits=4, decimal_places=2)),
                ('is_paid', models.BooleanField(default=False)),
                ('paid_date', models.DateTimeField(auto_now_add=True)),
                ('transaction_id', models.TextField(null=True, max_length=300, blank=True)),
                ('student', models.ForeignKey(verbose_name='Student', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Bill',
                'verbose_name_plural': 'Bills',
            },
        ),
    ]
