# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-11 11:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('arc_application', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='adultinhome',
            old_name='end_day',
            new_name='name_end_day',
        ),
        migrations.RenameField(
            model_name='adultinhome',
            old_name='end_month',
            new_name='name_end_month',
        ),
        migrations.RenameField(
            model_name='adultinhome',
            old_name='end_year',
            new_name='name_end_year',
        ),
        migrations.RenameField(
            model_name='adultinhome',
            old_name='start_day',
            new_name='name_start_day',
        ),
        migrations.RenameField(
            model_name='adultinhome',
            old_name='start_month',
            new_name='name_start_month',
        ),
        migrations.RenameField(
            model_name='adultinhome',
            old_name='start_year',
            new_name='name_start_year',
        ),
    ]
