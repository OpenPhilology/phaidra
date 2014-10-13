# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_auto_20141011_1719'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='content',
            name='related_topics',
        ),
    ]
