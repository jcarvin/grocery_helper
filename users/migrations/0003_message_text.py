# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-10 20:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_message_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='text',
            field=models.CharField(default='This was a fluke', max_length=2000),
            preserve_default=False,
        ),
    ]