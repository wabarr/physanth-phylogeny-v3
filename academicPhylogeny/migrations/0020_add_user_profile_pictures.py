# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-09-19 20:20
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('academicPhylogeny', '0019_fix_broken_links'),
    ]

    operations = [

        migrations.CreateModel(
            name='UserProfilePicture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(upload_to=b'')),
                ('associated_UserProfile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='academicPhylogeny.UserProfile')),
            ],
            options={
                'verbose_name': 'User Profile Picture',
                'verbose_name_plural': 'User Profile Pictures',
            },
        ),
    ]