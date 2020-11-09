# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-29 15:11
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('academicPhylogeny', '0015_auto_20170623_2311'),
    ]

    operations = [

        migrations.AddField(
            model_name='phd',
            name='submitter_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='phdupdate',
            name='submitter_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='submitter_user', to=settings.AUTH_USER_MODEL),
        ),
    ]