# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_content_related_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='related_content',
            field=models.ManyToManyField(help_text=b'Content that would help someone answer questions about this topic.', related_name=b'relates_to', null=True, to=b'app.Content', blank=True),
        ),
    ]
