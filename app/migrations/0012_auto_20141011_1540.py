# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_auto_20141011_1514'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grammar',
            name='tasks',
            field=models.ForeignKey(verbose_name=b'task sequence', blank=True, to='app.TaskSequence', null=True),
        ),
    ]
