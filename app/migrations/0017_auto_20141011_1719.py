# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_auto_20141011_1715'),
    ]

    operations = [
        migrations.AlterField(
            model_name='language',
            name='modern',
            field=models.BooleanField(default=True, help_text=b'Check this box if this is a modern language.', verbose_name=b'modern'),
        ),
    ]
