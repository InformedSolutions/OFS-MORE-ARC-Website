# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-02-08 11:59
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0002_delete_arcreview'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArcReview',
            fields=[
                ('application_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('user_id', models.CharField(max_length=50)),
                ('applicant_name', models.CharField(max_length=50)),
                ('app_type', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'ARC_REVIEW',
            },
        ),
    ]
