# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-09-21 03:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mdm', '0026_auto_20180921_1050'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job_data',
            name='workplace_1',
        ),
        migrations.RemoveField(
            model_name='job_data',
            name='workplace_2',
        ),
        migrations.RemoveField(
            model_name='job_data',
            name='workplace_3',
        ),
        migrations.RemoveField(
            model_name='job_data',
            name='workplace_4',
        ),
        migrations.RemoveField(
            model_name='job_data',
            name='workplace_5',
        ),
    ]
