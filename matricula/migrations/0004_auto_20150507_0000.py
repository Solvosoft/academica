# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ckeditor.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('matricula', '0003_enroll_enroll_activate'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('short_description', models.CharField(verbose_name='Short description', max_length=300)),
                ('description', models.TextField(verbose_name='Description')),
                ('amount', models.DecimalField(max_digits=4, verbose_name='Amount', decimal_places=2)),
                ('student', models.ForeignKey(verbose_name='Student', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Bills',
                'verbose_name': 'Bill',
            },
        ),
        migrations.AlterModelOptions(
            name='course',
            options={'verbose_name_plural': 'Courses', 'verbose_name': 'Course'},
        ),
        migrations.AlterModelOptions(
            name='enroll',
            options={'verbose_name_plural': 'Enrollments', 'verbose_name': 'Enrollment'},
        ),
        migrations.AlterModelOptions(
            name='group',
            options={'verbose_name_plural': 'Groups', 'verbose_name': 'Group'},
        ),
        migrations.AddField(
            model_name='enroll',
            name='bill_created',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='group',
            name='cost',
            field=models.DecimalField(max_digits=4, default=0.0, decimal_places=2, verbose_name='Course cost'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='course',
            name='content',
            field=ckeditor.fields.RichTextField(verbose_name='Content'),
        ),
        migrations.AlterField(
            model_name='course',
            name='name',
            field=models.CharField(verbose_name='Name', max_length=300),
        ),
        migrations.AlterField(
            model_name='enroll',
            name='enroll_activate',
            field=models.BooleanField(default=False, verbose_name='Is active for enroll?'),
        ),
        migrations.AlterField(
            model_name='enroll',
            name='enroll_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Enroll date'),
        ),
        migrations.AlterField(
            model_name='enroll',
            name='enroll_finished',
            field=models.BooleanField(default=False, verbose_name='Is enroll finished?'),
        ),
        migrations.AlterField(
            model_name='enroll',
            name='group',
            field=models.ForeignKey(verbose_name='Group', to='matricula.Group'),
        ),
        migrations.AlterField(
            model_name='enroll',
            name='student',
            field=models.ForeignKey(verbose_name='Student', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='group',
            name='course',
            field=models.ForeignKey(verbose_name='Course', to='matricula.Course'),
        ),
        migrations.AlterField(
            model_name='group',
            name='enroll_finish',
            field=models.DateTimeField(verbose_name='Enroll finish hour'),
        ),
        migrations.AlterField(
            model_name='group',
            name='enroll_start',
            field=models.DateTimeField(verbose_name='Enroll start hour'),
        ),
        migrations.AlterField(
            model_name='group',
            name='name',
            field=models.CharField(verbose_name='Name', max_length=50),
        ),
        migrations.AlterField(
            model_name='group',
            name='pre_enroll_finish',
            field=models.DateTimeField(verbose_name='Pre enroll finish hour'),
        ),
        migrations.AlterField(
            model_name='group',
            name='pre_enroll_start',
            field=models.DateTimeField(verbose_name='Pre enroll start hour'),
        ),
        migrations.AlterField(
            model_name='group',
            name='schedule',
            field=models.CharField(verbose_name='Schedule', max_length=300),
        ),
    ]
