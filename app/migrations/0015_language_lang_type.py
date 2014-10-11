# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_auto_20141011_1642'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='lang_type',
            field=models.CharField(default='modern', max_length=10, verbose_name=b'language type', choices=[(b'ancient', b'Ancient'), (b'modern', b'Modern')]),
            preserve_default=False,
        ),
    ]
