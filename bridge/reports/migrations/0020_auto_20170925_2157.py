# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-09-25 18:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [('reports', '0019_new_light_cache')]

    operations = [
        migrations.RemoveField(model_name='lightresource', name='component'),
        migrations.RemoveField(model_name='lightresource', name='report'),
        migrations.DeleteModel(name='LightResource')
    ]