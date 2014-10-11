# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20141011_1349'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sequence',
            name='grammar',
        ),
        migrations.RemoveField(
            model_name='sequence',
            name='task',
        ),
        migrations.RemoveField(
            model_name='grammar',
            name='tasks',
        ),
        migrations.DeleteModel(
            name='Sequence',
        ),
    ]
