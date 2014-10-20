# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_auto_20141011_1755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='graphic',
            field=models.CharField(help_text=b'\nImage within /static/images/ that \nshould be shown on lesson tiles \nwithin this category.\n', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='content',
            name='content',
            field=models.TextField(help_text=b'\nWrite this in <a href="https://github.com/\nOpenPhilology/phaidra/wiki/Phaidra-flavored-\nMarkdown" target="_blank">Phaidra-flavored \nMarkdown</a>.\n', verbose_name=b'Learning Content'),
        ),
        migrations.AlterField(
            model_name='content',
            name='grammar_ref',
            field=models.OneToOneField(null=True, to='app.Grammar', blank=True, help_text=b'\nThe morphology directly described by \nthis content.\n', verbose_name=b'grammar topic'),
        ),
        migrations.AlterField(
            model_name='content',
            name='related_content',
            field=models.ManyToManyField(help_text=b'\nContent that would help someone answer \nquestions about this topic.\n', related_name=b'relates_to', null=True, to=b'app.Content', blank=True),
        ),
        migrations.AlterField(
            model_name='content',
            name='source_lang',
            field=models.ForeignKey(related_name=b'content_written_in', to='app.Language', help_text=b'\nLanguage the content is written in.\n'),
        ),
        migrations.AlterField(
            model_name='content',
            name='title',
            field=models.CharField(help_text=b'\nShort, descriptive title of what \ncontent is in this section.\n', max_length=200, verbose_name=b'title'),
        ),
        migrations.AlterField(
            model_name='grammar',
            name='external_link',
            field=models.CharField(help_text=b'\nLink to section in the grammar book \nitself.\n', max_length=200, null=True, verbose_name=b'external url', blank=True),
        ),
        migrations.AlterField(
            model_name='grammar',
            name='query',
            field=models.CharField(help_text=b'\nDescribe the morphology of words that \nfit this grammar topic.\n', max_length=200, null=True, verbose_name=b'query string', blank=True),
        ),
        migrations.AlterField(
            model_name='grammar',
            name='ref',
            field=models.CharField(help_text=b"\nRefers to the section of the grammar \nbook you're using.\n", unique=True, max_length=10, verbose_name=b'Reference'),
        ),
        migrations.AlterField(
            model_name='grammar',
            name='title',
            field=models.CharField(help_text=b'\nShort, descriptive title of the grammar\nconcept.\n', max_length=200, verbose_name=b'title of grammar section'),
        ),
        migrations.AlterField(
            model_name='language',
            name='modern',
            field=models.BooleanField(default=True, help_text=b'\nCheck this box if this is a modern language.\n', verbose_name=b'modern'),
        ),
        migrations.AlterField(
            model_name='task',
            name='aspect',
            field=models.ManyToManyField(help_text=b"\nWhich aspect(s) of this user's knowledge \nis tested?\n", to=b'app.Aspect', verbose_name=b'knowledge aspect'),
        ),
        migrations.AlterField(
            model_name='task',
            name='endpoint',
            field=models.CharField(help_text=b'\nDefines the API endpoint to which the \nmorphological query should be appended.\n', max_length=20, verbose_name=b'API endpoint', choices=[(b'word', b'word'), (b'sentence', b'sentence'), (b'document', b'document')]),
        ),
        migrations.AlterField(
            model_name='task',
            name='hint_msg',
            field=models.CharField(help_text=b'\nMessage the user sees on their first \nincorrect attempt.\n', max_length=200, null=True, verbose_name=b'hint message', blank=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='name',
            field=models.CharField(help_text=b'\nShould corespond to something in <a \nhref="https://github.com/OpenPhilology/\nphaidra/tree/master/static/js/views/\nlessons/tasks" target="_blank">\nthis folder on Github</a>.\n', max_length=100, verbose_name=b'task name'),
        ),
        migrations.AlterField(
            model_name='task',
            name='success_msg',
            field=models.CharField(help_text=b'\nMessage the user sees on success.\n', max_length=200, null=True, verbose_name=b'success message', blank=True),
        ),
        migrations.AlterField(
            model_name='taskcontext',
            name='max_attempts',
            field=models.IntegerField(help_text=b'\nMaximum number of times user should be \npresented with this task before moving \non to the next.\n', verbose_name=b'maximum attempts'),
        ),
        migrations.AlterField(
            model_name='taskcontext',
            name='order',
            field=models.IntegerField(help_text=b'\nOrder of this task in the defined sequence.\n'),
        ),
        migrations.AlterField(
            model_name='taskcontext',
            name='target_accuracy',
            field=models.FloatField(help_text=b'\nDecimal between 0 and 1. When a user \nreaches this level of accuracy, \nthey move to the next task.\n', verbose_name=b'target accuracy'),
        ),
        migrations.AlterField(
            model_name='taskcontext',
            name='task',
            field=models.ForeignKey(verbose_name=b'task', to='app.Task', help_text=b'\nTask that belongs in the sequence at \nthis point.\n'),
        ),
        migrations.AlterField(
            model_name='taskcontext',
            name='task_sequence',
            field=models.ForeignKey(verbose_name=b'task sequence', to='app.TaskSequence', help_text=b'\nThe task sequence to which task, with \nthis metadata, belongs.\n'),
        ),
        migrations.AlterField(
            model_name='tasksequence',
            name='name',
            field=models.CharField(help_text=b'\nName of this unique set and order of tasks. \n(e.g. "Beginner Nouns" or "Learn to Read Greek")\n', max_length=200, verbose_name=b'task sequence name'),
        ),
    ]
