# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_auto_20141011_1354'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskContext',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('target_accuracy', models.FloatField(help_text=b'Decimal between 0 and 1. When a user reaches this level of accuracy, they move to the next task.', verbose_name=b'target accuracy')),
                ('max_attempts', models.IntegerField(help_text=b'Maximum number of times user should be presented with this task before moving on to the next.', verbose_name=b'maximum attempts')),
                ('order', models.IntegerField(help_text=b'Order of this task in the defined sequence.')),
                ('task', models.ForeignKey(verbose_name=b'task', to='app.Task', help_text=b'Task that belongs in the sequence at this point.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaskSequence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'Name of this unique set and order of tasks. (e.g. "Beginner Nouns" or "Learn to Read Greek")', max_length=200, verbose_name=b'task sequence name')),
                ('tasks', models.ManyToManyField(to='app.Task', through='app.TaskContext')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='taskcontext',
            name='task_sequence',
            field=models.ForeignKey(verbose_name=b'task sequence', to='app.TaskSequence', help_text=b'The task sequence to which task, with this metadata, belongs.'),
            preserve_default=True,
        ),
        migrations.AlterModelOptions(
            name='grammar',
            options={'ordering': ['title'], 'verbose_name': 'Grammar Topic'},
        ),
        migrations.AddField(
            model_name='category',
            name='graphic',
            field=models.CharField(help_text=b'Image within /static/images/ that should be shown on lesson tiles within this category.', max_length=200, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='grammar',
            name='tasks',
            field=models.ForeignKey(blank=True, to='app.TaskSequence', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='appuser',
            name='lang_learning',
            field=models.ForeignKey(related_name=b'learning', to='app.Language', help_text=b'Language the user is learning.', null=True),
        ),
        migrations.AlterField(
            model_name='appuser',
            name='lang_speaking',
            field=models.ForeignKey(related_name=b'speaking', to='app.Language', help_text=b'Language teh user speaks.', null=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=200, verbose_name=b'category name'),
        ),
        migrations.AlterField(
            model_name='content',
            name='source_lang',
            field=models.ForeignKey(related_name=b'content_written_in', to='app.Language', help_text=b'Language the content is written in.'),
        ),
        migrations.AlterField(
            model_name='content',
            name='target_lang',
            field=models.ForeignKey(related_name=b'content_written_about', to='app.Language', help_text=b'Language the content teaches.'),
        ),
        migrations.AlterField(
            model_name='content',
            name='title',
            field=models.CharField(help_text=b'Short, descriptive title of what content is in this section.', max_length=200, verbose_name=b'title'),
        ),
        migrations.AlterField(
            model_name='grammar',
            name='category',
            field=models.ForeignKey(blank=True, to='app.Category', null=True),
        ),
        migrations.AlterField(
            model_name='grammar',
            name='external_link',
            field=models.CharField(help_text=b'Link to section in the grammar book itself.', max_length=200, null=True, verbose_name=b'external url', blank=True),
        ),
        migrations.AlterField(
            model_name='grammar',
            name='query',
            field=models.CharField(help_text=b'Describe the morphology of words that fit this grammar topic.', max_length=200, null=True, verbose_name=b'query string', blank=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='endpoint',
            field=models.CharField(help_text=b'Defines the API endpoint to which the morphological query should be appended.', max_length=20, verbose_name=b'API endpoint', choices=[(b'word', b'word'), (b'sentence', b'sentence'), (b'document', b'document')]),
        ),
        migrations.AlterField(
            model_name='task',
            name='hint_msg',
            field=models.CharField(help_text=b'Message the user sees on their first incorrect attempt.', max_length=200, null=True, verbose_name=b'hint message', blank=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='name',
            field=models.CharField(help_text=b'Should correspond to something in <a href="https://github.com/OpenPhilology/phaidra/tree/master/static/js/views/lessons/tasks" target="_blank">this folder on Github</a>.', max_length=100, verbose_name=b'task name'),
        ),
        migrations.AlterField(
            model_name='task',
            name='success_msg',
            field=models.CharField(help_text=b'Message the user sees on success.', max_length=200, null=True, verbose_name=b'success message', blank=True),
        ),
    ]
