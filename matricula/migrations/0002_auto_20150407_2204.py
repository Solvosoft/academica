# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ckeditor.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('matricula', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=300)),
                ('content', ckeditor.fields.RichTextField()),
            ],
        ),
        migrations.CreateModel(
            name='Enroll',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('enroll_finished', models.BooleanField(default=False)),
                ('enroll_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('schedule', models.CharField(max_length=300)),
                ('pre_enroll_start', models.DateTimeField()),
                ('pre_enroll_finish', models.DateTimeField()),
                ('enroll_start', models.DateTimeField()),
                ('enroll_finish', models.DateTimeField()),
                ('course', models.ForeignKey(to='matricula.Course')),
            ],
        ),
        migrations.AddField(
            model_name='enroll',
            name='group',
            field=models.ForeignKey(to='matricula.Group'),
        ),
        migrations.AddField(
            model_name='enroll',
            name='student',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
