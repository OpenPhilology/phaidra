# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0024_auto_20141117_1935'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='graphic',
        ),
        migrations.RemoveField(
            model_name='task',
            name='hint_msg',
        ),
        migrations.RemoveField(
            model_name='task',
            name='success_msg',
        ),
        migrations.RemoveField(
            model_name='taskcontext',
            name='max_attempts',
        ),
        migrations.RemoveField(
            model_name='taskcontext',
            name='target_accuracy',
        ),
        migrations.AddField(
            model_name='taskcontext',
            name='hint_msg',
            field=models.CharField(help_text=b'\nMessage the user sees on their first \nincorrect attempt.\n', max_length=200, null=True, verbose_name=b'hint message', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='taskcontext',
            name='success_msg',
            field=models.CharField(help_text=b'\nMessage the user sees on success.\n', max_length=200, null=True, verbose_name=b'success message', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tasksequence',
            name='max_attempts',
            field=models.IntegerField(default=5, help_text=b'\nMaximum number of times user should be \npresented with this sequence before moving \non to the next grammar topic.\n<br><br>\nA value of 0 indicates that the user should\ncontinue to try this sequence until reaching\nthe target accuracy.\n', verbose_name=b'maximum attempts'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tasksequence',
            name='min_attempts',
            field=models.IntegerField(default=1, help_text=b'\nMinimum number of times user should be \npresented with this sequence before moving \non to the next grammar topic.\n', verbose_name=b'minimum attempts'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tasksequence',
            name='target_accuracy',
            field=models.IntegerField(default=60, help_text=b'\nDecimal between 1 and 100. When a user \nreaches this level of accuracy, \nthey move to the next grammar topic.\n', verbose_name=b'target accuracy'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(help_text=b'Affects the ring color around task', max_length=200, verbose_name=b'category name'),
        ),
    ]
