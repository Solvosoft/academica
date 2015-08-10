# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('matricula', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Classroom',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=30)),
                ('capacity', models.IntegerField()),
                ('selection_score', models.IntegerField(choices=[(5, 'High priority'), (4, 'Priority'), (3, 'Normal'), (2, 'Low priority'), (1, 'Last assigned')])),
            ],
        ),
        migrations.CreateModel(
            name='ClassroomGroupProfesor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('Classroom', models.ForeignKey(to='matricula.Classroom')),
            ],
        ),
        migrations.CreateModel(
            name='ClassroomSchedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('classroom', models.ForeignKey(to='matricula.Classroom')),
            ],
        ),
        migrations.CreateModel(
            name='ClassroomType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(verbose_name='Name', max_length=30)),
                ('description', models.CharField(verbose_name='Description', max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Hour',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('day_position', models.SmallIntegerField(validators=[django.core.validators.MaxValueValidator(168), django.core.validators.MinValueValidator(0)])),
                ('description', models.TextField()),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profesor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('number_hours', models.SmallIntegerField(verbose_name='Number of work hours ')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProfesorSchedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
            ],
        ),
        migrations.CreateModel(
            name='Week',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('hours', models.ManyToManyField(to='matricula.Hour')),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='required_courses',
            field=models.ManyToManyField(verbose_name='Level', related_name='required_courses_rel_+', to='matricula.Course'),
        ),
        migrations.AddField(
            model_name='group',
            name='number_days',
            field=models.SmallIntegerField(verbose_name='Number of imparting days', default=1, validators=[django.core.validators.MaxValueValidator(7), django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='group',
            name='number_hours',
            field=models.IntegerField(verbose_name='Number of lesson hours', default=1, validators=[django.core.validators.MaxValueValidator(168), django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='period',
            name='active',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='group',
            name='schedule',
            field=models.ForeignKey(to='matricula.Week', null=True),
        ),
        migrations.AddField(
            model_name='profesorschedule',
            name='period',
            field=models.ForeignKey(to='matricula.Period'),
        ),
        migrations.AddField(
            model_name='profesorschedule',
            name='profesor',
            field=models.ForeignKey(to='matricula.Profesor'),
        ),
        migrations.AddField(
            model_name='profesorschedule',
            name='schedule',
            field=models.ForeignKey(to='matricula.Week', null=True),
        ),
        migrations.AddField(
            model_name='classroomschedule',
            name='period',
            field=models.ForeignKey(to='matricula.Period'),
        ),
        migrations.AddField(
            model_name='classroomschedule',
            name='schedule',
            field=models.ForeignKey(to='matricula.Week', null=True),
        ),
        migrations.AddField(
            model_name='classroomgroupprofesor',
            name='group',
            field=models.ForeignKey(to='matricula.Group'),
        ),
        migrations.AddField(
            model_name='classroomgroupprofesor',
            name='period',
            field=models.ForeignKey(to='matricula.Period'),
        ),
        migrations.AddField(
            model_name='classroomgroupprofesor',
            name='profesor',
            field=models.ForeignKey(to='matricula.Profesor'),
        ),
        migrations.AddField(
            model_name='classroomgroupprofesor',
            name='schedule',
            field=models.ForeignKey(to='matricula.Week', null=True),
        ),
        migrations.AddField(
            model_name='classroom',
            name='classroom_type',
            field=models.ForeignKey(to='matricula.ClassroomType'),
        ),
        migrations.AddField(
            model_name='group',
            name='classroom_type',
            field=models.ForeignKey(verbose_name='Classroom type', null=True, to='matricula.ClassroomType'),
        ),
    ]
