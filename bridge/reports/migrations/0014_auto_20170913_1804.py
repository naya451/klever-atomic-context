# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-09-13 15:04
from __future__ import unicode_literals

from django.db import migrations, models
import reports.models


class Migration(migrations.Migration):

    dependencies = [('reports', '0013_auto_20170913_1801')]

    operations = [
        migrations.RenameField(model_name='reportcomponent', old_name='coverage_arch', new_name='coverage'),
        migrations.RenameField(model_name='reportcomponent', old_name='archive', new_name='log'),
        migrations.RenameField(model_name='reportsafe', old_name='archive', new_name='proof'),
        migrations.RenameField(model_name='reportunknown', old_name='archive', new_name='problem_description'),
        migrations.RenameField(model_name='reportunsafe', old_name='archive', new_name='error_trace'),
        migrations.AddField(
            model_name='reportcomponent', name='verifier_input',
            field=models.FileField(null=True, upload_to=reports.models.get_component_path),
        ),
    ]
