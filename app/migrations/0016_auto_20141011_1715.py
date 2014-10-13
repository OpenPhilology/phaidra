# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_language_lang_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='language',
            name='lang_type',
        ),
        migrations.AddField(
            model_name='language',
            name='modern',
            field=models.BooleanField(default=True, help_text=b'Check this box if this is a modern language.', verbose_name=b'modern'),
            preserve_default=False,
        ),
    ]
