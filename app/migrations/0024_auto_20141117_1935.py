# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_auto_20141020_1541'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grammar',
            name='ref',
            field=models.CharField(help_text=b"\nRefers to the section of the grammar \nbook you're using (e.g. s6 for Smyth,\nsection 6). Must be unique. <br><br> \n<b>FYI:</b>\nOnce created, this field is read-only,\nbecause it's used to calculate user\nprogress.\n", max_length=10, verbose_name=b'Reference'),
        ),
    ]
