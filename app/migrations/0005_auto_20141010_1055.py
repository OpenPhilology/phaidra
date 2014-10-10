# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_content_related_topics'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='grammar_ref',
            field=models.OneToOneField(null=True, blank=True, to='app.Grammar', verbose_name=b'corresponding grammar reference'),
        ),
    ]
