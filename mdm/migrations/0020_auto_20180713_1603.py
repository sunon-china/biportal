# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-13 08:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mdm', '0019_auto_20180713_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job_data',
            name='dept_key',
            field=models.ForeignKey(db_column='dept_key', default='', on_delete=django.db.models.deletion.CASCADE, related_name='dept', to='mdm.Department', to_field='key'),
        ),
    ]
