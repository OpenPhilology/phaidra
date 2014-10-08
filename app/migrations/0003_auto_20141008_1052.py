# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20141008_1048'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='grammar',
            options={'ordering': ['title']},
        ),
        migrations.AlterField(
            model_name='content',
            name='grammar_ref',
            field=models.ForeignKey(verbose_name=b'corresponding grammar reference', blank=True, to='app.Grammar', null=True),
        ),
        migrations.AlterField(
            model_name='grammar',
            name='external_link',
            field=models.CharField(max_length=200, null=True, verbose_name=b'external url for reference lookup', blank=True),
        ),
        migrations.AlterField(
            model_name='grammar',
            name='query',
            field=models.CharField(max_length=200, null=True, verbose_name=b'query string', blank=True),
        ),
    ]
