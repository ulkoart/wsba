# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-21 11:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('presentations', '0011_auto_20160321_1103'),
    ]

    operations = [
        migrations.RenameField(
            model_name='answer',
            old_name='variant_number',
            new_name='position',
        ),
    ]
