# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20141008_1052'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='related_topics',
            field=models.ManyToManyField(related_name=b'relates_to', null=True, verbose_name=b'related grammar topics', to='app.Grammar', blank=True),
            preserve_default=True,
        ),
    ]
