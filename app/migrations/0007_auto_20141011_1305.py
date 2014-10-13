# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20141010_1556'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='content',
            field=models.TextField(help_text=b'Write this in <a href="https://github.com/OpenPhilology/phaidra/wiki/Phaidra-flavored-Markdown" target="_blank">Phaidra-flavored Markdown</a>.', verbose_name=b'Learning Content'),
        ),
        migrations.AlterField(
            model_name='content',
            name='grammar_ref',
            field=models.OneToOneField(null=True, to='app.Grammar', blank=True, help_text=b'The morphology directly described by this content.', verbose_name=b'grammar topic'),
        ),
        migrations.AlterField(
            model_name='content',
            name='related_topics',
            field=models.ManyToManyField(related_name=b'Topics that would help someone answer questions about this topic (e.g. "Intro to Verbs" is related to "The Aorist Tense").', null=True, verbose_name=b'related grammar topics', to=b'app.Grammar', blank=True),
        ),
        migrations.AlterField(
            model_name='content',
            name='source_lang',
            field=models.ForeignKey(related_name=b'content_written_in', to='app.Language', help_text=b'Language the content is written in'),
        ),
        migrations.AlterField(
            model_name='content',
            name='target_lang',
            field=models.ForeignKey(related_name=b'content_written_about', to='app.Language', help_text=b'Language the content is teaching'),
        ),
        migrations.AlterField(
            model_name='content',
            name='title',
            field=models.CharField(help_text=b'Short, descriptive title of what content is in this section', max_length=200, verbose_name=b'title'),
        ),
        migrations.AlterField(
            model_name='grammar',
            name='external_link',
            field=models.CharField(help_text=b'Link to section in the grammar book itself', max_length=200, null=True, verbose_name=b'external url', blank=True),
        ),
        migrations.AlterField(
            model_name='grammar',
            name='query',
            field=models.CharField(help_text=b'Describe the morphology of words that fit this grammar topic', max_length=200, null=True, verbose_name=b'query string', blank=True),
        ),
        migrations.AlterField(
            model_name='grammar',
            name='ref',
            field=models.CharField(help_text=b"Refers to the section of the grammar book you're using.", unique=True, max_length=10, verbose_name=b'Reference'),
        ),
        migrations.AlterField(
            model_name='grammar',
            name='title',
            field=models.CharField(help_text=b'Short, descriptive title of the grammar concept.', max_length=200, verbose_name=b'title of grammar section'),
        ),
        migrations.AlterField(
            model_name='language',
            name='local_name',
            field=models.CharField(help_text=b'(e.g. Deutsch)', max_length=200, verbose_name=b'language name'),
        ),
        migrations.AlterField(
            model_name='language',
            name='locale',
            field=models.CharField(help_text=b'(e.g. de-at)', max_length=5, verbose_name=b'language code'),
        ),
        migrations.AlterField(
            model_name='language',
            name='name',
            field=models.CharField(help_text=b'(e.g. German)', max_length=200, verbose_name=b'language name (english)'),
        ),
        migrations.AlterField(
            model_name='language',
            name='short_code',
            field=models.CharField(help_text=b"(e.g. 'de')", max_length=5, verbose_name=b'shortcode'),
        ),
    ]
