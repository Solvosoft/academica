# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import simple_email_confirmation.models
import django.utils.timezone
import ckeditor.fields
from django.conf import settings
import django.contrib.auth.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], verbose_name='username', unique=True, max_length=30, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', error_messages={'unique': 'A user with that username already exists.'})),
                ('first_name', models.CharField(max_length=30, blank=True, verbose_name='first name')),
                ('last_name', models.CharField(max_length=30, blank=True, verbose_name='last name')),
                ('email', models.EmailField(max_length=254, blank=True, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
            ],
            options={
                'verbose_name_plural': 'users',
                'verbose_name': 'user',
                'abstract': False,
            },
            bases=(simple_email_confirmation.models.SimpleEmailConfirmationUserMixin, models.Model),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=300, verbose_name='Name')),
                ('description', ckeditor.fields.RichTextField(verbose_name='Description')),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'verbose_name': 'Category',
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=300, verbose_name='Name')),
                ('content', ckeditor.fields.RichTextField(verbose_name='Content')),
                ('category', models.ForeignKey(to='matricula.Category', verbose_name='Category')),
            ],
            options={
                'verbose_name_plural': 'Courses',
                'verbose_name': 'Course',
            },
        ),
        migrations.CreateModel(
            name='Enroll',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('enroll_finished', models.BooleanField(verbose_name='Is enroll finished?', default=False)),
                ('enroll_activate', models.BooleanField(verbose_name='Is active for enroll?', default=False)),
                ('enroll_date', models.DateTimeField(auto_now_add=True, verbose_name='Enroll date')),
                ('bill_created', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Enrollments',
                'verbose_name': 'Enrollment',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('schedule', models.CharField(max_length=300, verbose_name='Schedule')),
                ('pre_enroll_start', models.DateTimeField(verbose_name='Pre enroll start hour')),
                ('pre_enroll_finish', models.DateTimeField(verbose_name='Pre enroll finish hour')),
                ('enroll_start', models.DateTimeField(verbose_name='Enroll start hour')),
                ('enroll_finish', models.DateTimeField(verbose_name='Enroll finish hour')),
                ('cost', models.DecimalField(decimal_places=2, verbose_name='Course cost', max_digits=4)),
                ('maximum', models.SmallIntegerField(verbose_name='Maximum number of students')),
                ('course', models.ForeignKey(to='matricula.Course', verbose_name='Course')),
            ],
            options={
                'verbose_name_plural': 'Groups',
                'verbose_name': 'Group',
            },
        ),
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('start_date', models.DateField(verbose_name='Period start date')),
                ('finish_date', models.DateField(verbose_name='Period finish date')),
            ],
            options={
                'verbose_name_plural': 'Periods',
                'verbose_name': 'Period',
            },
        ),
        migrations.AddField(
            model_name='group',
            name='period',
            field=models.ForeignKey(to='matricula.Period', verbose_name='Period'),
        ),
        migrations.AddField(
            model_name='enroll',
            name='group',
            field=models.ForeignKey(to='matricula.Group', verbose_name='Group'),
        ),
        migrations.AddField(
            model_name='enroll',
            name='student',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Student'),
        ),
        migrations.AddField(
            model_name='student',
            name='groups',
            field=models.ManyToManyField(related_name='user_set', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups', to='auth.Group', blank=True, related_query_name='user'),
        ),
        migrations.AddField(
            model_name='student',
            name='user_permissions',
            field=models.ManyToManyField(related_name='user_set', help_text='Specific permissions for this user.', verbose_name='user permissions', to='auth.Permission', blank=True, related_query_name='user'),
        ),
    ]
