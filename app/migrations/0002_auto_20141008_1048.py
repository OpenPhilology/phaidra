# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='grammar_ref',
            field=models.ForeignKey(verbose_name=b'corresponding grammar reference', to='app.Grammar', null=True),
        ),
    ]
