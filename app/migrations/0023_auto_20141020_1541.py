# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0022_auto_20141020_1538'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='grammar_ref',
            field=models.ForeignKey(blank=True, to='app.Grammar', help_text=b'\nThe morphology directly described by \nthis content.\n', null=True, verbose_name=b'grammar topic'),
        ),
    ]
