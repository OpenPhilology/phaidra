# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20141011_1305'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aspect',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'', max_length=1, verbose_name=b'aspect name')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sequence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('target_accuracy', models.FloatField(help_text=b'Decimal between 0 and 1. When a user reaches this level of accuracy, they move to the next task.', verbose_name=b'target accuracy')),
                ('max_attempts', models.IntegerField(help_text=b'Maximum number of times user should be presented with this task before moving on to the next.', verbose_name=b'maximum attempts')),
                ('grammar', models.ForeignKey(verbose_name=b'grammar topic', to='app.Grammar', help_text=b'Grammar topic the task is assigned to')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'Should correspond to something in <a href="https://github.com/OpenPhilology/phaidra/tree/master/static/js/views/lessons/tasks" taget="_blank">this folder on Github</a>.', max_length=100, verbose_name=b'task name')),
                ('endpoint', models.CharField(help_text=b'Defines the API endpoint to which the morphological query should be appended', max_length=20, verbose_name=b'API endpoint', choices=[(b'word', b'word'), (b'sentence', b'sentence'), (b'document', b'document')])),
                ('success_msg', models.CharField(help_text=b'Message the user sees on success.', max_length=200, verbose_name=b'success message')),
                ('hint_msg', models.CharField(help_text=b'Message the user sees on their first incorrect attempt.', max_length=200, verbose_name=b'hint message')),
                ('aspect', models.ManyToManyField(help_text=b"Which aspect(s) of this user's knowledge is tested?", to='app.Aspect', verbose_name=b'knowledge aspect')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='sequence',
            name='task',
            field=models.ForeignKey(verbose_name=b'task', to='app.Task', help_text=b'Task that the grammar topic is applied to'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='grammar',
            name='tasks',
            field=models.ManyToManyField(to='app.Task', through='app.Sequence'),
            preserve_default=True,
        ),
    ]
