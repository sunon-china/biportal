# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-10 08:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mdm', '0011_company_parent_company_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='parent_company_key',
            field=models.ForeignKey(db_column='parent_company_key', default='', on_delete=django.db.models.deletion.CASCADE, to='mdm.Company'),
        ),
    ]
