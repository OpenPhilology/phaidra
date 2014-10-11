# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_auto_20141011_1339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aspect',
            name='name',
            field=models.CharField(help_text=b'', max_length=1, verbose_name=b'aspect name', choices=[(b'V', b'Vocabulary'), (b'S', b'Syntax'), (b'M', b'Morphology')]),
        ),
    ]
