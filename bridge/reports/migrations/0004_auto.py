# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-20 12:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_update_verifier_time'),
    ]

    operations = [
        migrations.RemoveField(model_name='reportroot', name='safes'),
        migrations.AddField(model_name='reportcomponent', name='verification', field=models.BooleanField(default=False))
    ]