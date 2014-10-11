# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_auto_20141011_1540'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='direction',
            field=models.CharField(default='ltr', max_length=3, verbose_name=b'text direction', choices=[(b'ltr', b'Left-to-right'), (b'rtl', b'Right-to-left')]),
            preserve_default=False,
        ),
    ]
