# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('matricula', '0009_group_flow'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuTranslations',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('language', models.CharField(max_length=3, choices=[('es', 'Spanish'), ('en', 'English')], default='es', verbose_name='Language')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('menu', models.ForeignKey(to='matricula.MenuItem', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MultilingualContent',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('language', models.CharField(max_length=3, choices=[('es', 'Spanish'), ('en', 'English')], default='es', verbose_name='Language')),
                ('title', models.CharField(max_length=300, blank=True, null=True)),
                ('content', ckeditor.fields.RichTextField(verbose_name='Content')),
            ],
        ),
        migrations.RemoveField(
            model_name='page',
            name='content',
        ),
        migrations.AddField(
            model_name='multilingualcontent',
            name='page',
            field=models.ForeignKey(to='matricula.Page'),
        ),
    ]
