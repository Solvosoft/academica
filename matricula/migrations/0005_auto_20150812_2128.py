# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('matricula', '0004_auto_20150810_0045'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='classroom',
            options={'verbose_name_plural': 'Classrooms', 'verbose_name': 'Classroom'},
        ),
        migrations.AlterModelOptions(
            name='classroomgroupprofesor',
            options={'verbose_name_plural': 'Asignations', 'verbose_name': 'Asignation'},
        ),
        migrations.AlterModelOptions(
            name='classroomtype',
            options={'verbose_name_plural': 'Classroom Types', 'verbose_name': 'Classroom Type'},
        ),
        migrations.AlterModelOptions(
            name='profesor',
            options={'verbose_name_plural': 'Profesors', 'verbose_name': 'Profesor'},
        ),
        migrations.AlterField(
            model_name='classroom',
            name='capacity',
            field=models.IntegerField(verbose_name='Capacity'),
        ),
        migrations.AlterField(
            model_name='classroom',
            name='classroom_type',
            field=models.ForeignKey(verbose_name='Classroom type', to='matricula.ClassroomType'),
        ),
        migrations.AlterField(
            model_name='classroom',
            name='name',
            field=models.CharField(max_length=30, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='classroom',
            name='selection_score',
            field=models.IntegerField(verbose_name='Selection priority', choices=[(5, 'High priority'), (4, 'Priority'), (3, 'Normal'), (2, 'Low priority'), (1, 'Last assigned')]),
        ),
        migrations.AlterField(
            model_name='classroomgroupprofesor',
            name='classroom',
            field=models.ForeignKey(verbose_name='Classroom', to='matricula.Classroom'),
        ),
        migrations.AlterField(
            model_name='classroomgroupprofesor',
            name='group',
            field=models.ForeignKey(verbose_name='Group', to='matricula.Group'),
        ),
        migrations.AlterField(
            model_name='classroomgroupprofesor',
            name='period',
            field=models.ForeignKey(verbose_name='Period', to='matricula.Period'),
        ),
        migrations.AlterField(
            model_name='classroomgroupprofesor',
            name='profesor',
            field=models.ForeignKey(verbose_name='Profesor', to='matricula.Profesor'),
        ),
        migrations.AlterField(
            model_name='classroomgroupprofesor',
            name='schedule',
            field=models.ForeignKey(verbose_name='Schedule', to='matricula.Week', null=True),
        ),
        migrations.AlterField(
            model_name='group',
            name='schedule',
            field=models.ForeignKey(to='matricula.Week', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profesor',
            name='number_hours',
            field=models.SmallIntegerField(verbose_name='Number of work hours'),
        ),
        migrations.AlterField(
            model_name='profesor',
            name='user',
            field=models.OneToOneField(verbose_name='User', to=settings.AUTH_USER_MODEL),
        ),
    ]
