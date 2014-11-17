# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0025_auto_20141117_1955'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taskcontext',
            name='hint_msg',
        ),
        migrations.RemoveField(
            model_name='taskcontext',
            name='success_msg',
        ),
        migrations.AlterField(
            model_name='tasksequence',
            name='max_attempts',
            field=models.IntegerField(help_text=b'\nMaximum number of times user should be \npresented with this sequence before moving \non to the next grammar topic.\n<br><br>\nA value of 0 indicates that the user should\ncontinue to try this sequence until reaching\nthe target accuracy.\n', null=True, verbose_name=b'maximum attempts', blank=True),
        ),
        migrations.AlterField(
            model_name='tasksequence',
            name='min_attempts',
            field=models.IntegerField(help_text=b'\nMinimum number of times user should be \npresented with this sequence before moving \non to the next grammar topic.\n', null=True, verbose_name=b'minimum attempts', blank=True),
        ),
        migrations.AlterField(
            model_name='tasksequence',
            name='target_accuracy',
            field=models.IntegerField(help_text=b'\nDecimal between 1 and 100. When a user \nreaches this level of accuracy, \nthey move to the next grammar topic.\n', null=True, verbose_name=b'target accuracy', blank=True),
        ),
    ]
