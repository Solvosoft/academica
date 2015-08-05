# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import simple_email_confirmation.models
import django.contrib.auth.models
import django.core.validators
import ckeditor.fields
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', default=False, verbose_name='superuser status')),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=30, error_messages={'unique': 'A user with that username already exists.'}, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], unique=True, verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(help_text='Designates whether the user can log into this admin site.', default=False, verbose_name='staff status')),
                ('is_active', models.BooleanField(help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', default=True, verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
            ],
            options={
                'verbose_name_plural': 'users',
                'abstract': False,
                'verbose_name': 'user',
            },
            bases=(simple_email_confirmation.models.SimpleEmailConfirmationUserMixin, models.Model),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enroll_finished', models.BooleanField(default=False, verbose_name='Is enroll finished?')),
                ('enroll_activate', models.BooleanField(default=False, verbose_name='Is active for enroll?')),
                ('enroll_date', models.DateTimeField(auto_now_add=True, verbose_name='Enroll date')),
                ('bill_created', models.BooleanField(default=False, verbose_name='Bill created')),
            ],
            options={
                'verbose_name_plural': 'Enrollments',
                'verbose_name': 'Enrollment',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('schedule', models.CharField(max_length=300, verbose_name='Schedule')),
                ('pre_enroll_start', models.DateTimeField(verbose_name='Pre enroll start hour')),
                ('pre_enroll_finish', models.DateTimeField(verbose_name='Pre enroll finish hour')),
                ('enroll_start', models.DateTimeField(verbose_name='Enroll start hour')),
                ('enroll_finish', models.DateTimeField(verbose_name='Enroll finish hour')),
                ('currency', models.CharField(choices=[('USD', 'US Dollar'), ('EUR', 'Euro'), ('CRC', 'Costa Rican Colon')], max_length=3, default='CRC', verbose_name='Currency')),
                ('cost', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Course cost')),
                ('maximum', models.SmallIntegerField(verbose_name='Maximum number of students')),
                ('is_open', models.BooleanField(default=True)),
                ('flow', models.SmallIntegerField(choices=[(0, 'Normal flow (manual enroll activate)'), (1, 'Auto pre-enroll (automatic enroll activate)'), (2, 'Auto enroll (automatic enroll finished)')], default=0, verbose_name='Enrollment behavior')),
                ('course', models.ForeignKey(to='matricula.Course', verbose_name='Course')),
            ],
            options={
                'verbose_name_plural': 'Groups',
                'verbose_name': 'Group',
            },
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('type', models.SmallIntegerField(choices=[(0, 'Internal'), (1, 'Page')], default=0, verbose_name='Type')),
                ('description', models.CharField(max_length=50, verbose_name='Description')),
                ('require_authentication', models.BooleanField(default=False, verbose_name='Authentication is required')),
                ('order', models.SmallIntegerField(verbose_name='Menu order')),
                ('publicated', models.BooleanField(default=True, verbose_name='Publicated')),
                ('is_index', models.BooleanField(default=False, verbose_name='Index page')),
                ('parent', models.ForeignKey(blank=True, null=True, to='matricula.MenuItem', verbose_name='Page parent')),
            ],
            options={
                'verbose_name_plural': 'Menu Items',
                'verbose_name': 'Menu Item',
            },
        ),
        migrations.CreateModel(
            name='MenuTranslations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(choices=[('es', 'Spanish'), ('en', 'English')], max_length=3, default='es', verbose_name='Language')),
                ('name', models.CharField(max_length=50, verbose_name='Description')),
                ('menu', models.ForeignKey(null=True, to='matricula.MenuItem')),
            ],
        ),
        migrations.CreateModel(
            name='MultilingualContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(choices=[('es', 'Spanish'), ('en', 'English')], max_length=3, default='es', verbose_name='Language')),
                ('title', models.CharField(blank=True, null=True, max_length=300)),
                ('content', ckeditor.fields.RichTextField(verbose_name='Content')),
            ],
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField()),
            ],
            options={
                'verbose_name_plural': 'Pages',
                'verbose_name': 'Page',
            },
        ),
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
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
            model_name='multilingualcontent',
            name='page',
            field=models.ForeignKey(to='matricula.Page'),
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
            field=models.ManyToManyField(help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', blank=True, related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='student',
            name='user_permissions',
            field=models.ManyToManyField(help_text='Specific permissions for this user.', blank=True, related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
