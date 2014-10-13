# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_language_direction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appuser',
            name='lang_learning',
            field=models.ForeignKey(related_name=b'learning', verbose_name=b'Learning Language', to='app.Language', help_text=b'Language the user is learning.', null=True),
        ),
        migrations.AlterField(
            model_name='appuser',
            name='lang_speaking',
            field=models.ForeignKey(related_name=b'speaking', verbose_name=b'Speaks Language', to='app.Language', help_text=b'Language the user speaks.', null=True),
        ),
    ]
