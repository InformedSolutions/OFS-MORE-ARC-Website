# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-28 11:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('arc_application', '0002_auto_20180228_1042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='arccomments',
            name='table_pk',
            field=models.UUIDField(blank=True),
        ),
    ]
