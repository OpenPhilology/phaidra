# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_remove_content_related_topics'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='related_content',
            field=models.ManyToManyField(help_text=b'Content that would help someone answer questions about this topic.', related_name='related_content_rel_+', null=True, to='app.Content', blank=True),
            preserve_default=True,
        ),
    ]
