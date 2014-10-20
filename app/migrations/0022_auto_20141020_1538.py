# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_auto_20141020_1530'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grammar',
            name='ref',
            field=models.CharField(help_text=b"\nRefers to the section of the grammar \nbook you're using.\n", max_length=10, verbose_name=b'Reference'),
        ),
    ]
