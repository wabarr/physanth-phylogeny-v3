# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-19 20:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academicPhylogeny', '0003_auto_20170519_2008'),
    ]

    operations = [
        migrations.AddField(
            model_name='phd',
            name='validated',
            field=models.BooleanField(default=False),
        ),
    ]
