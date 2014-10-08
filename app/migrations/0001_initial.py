# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, max_length=30, verbose_name='username', validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.', 'invalid')])),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=75, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, verbose_name=b'title of contents')),
                ('content', models.TextField(verbose_name=b'content written in markdown')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Grammar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ref', models.CharField(unique=True, max_length=10, verbose_name=b'reference to the grammar book section')),
                ('external_link', models.CharField(max_length=200, verbose_name=b'external url for reference lookup')),
                ('query', models.CharField(max_length=200, verbose_name=b'query string')),
                ('title', models.CharField(max_length=200, verbose_name=b'title of grammar section')),
                ('category', models.ForeignKey(to='app.Category')),
            ],
            options={
                'ordering': ['ref'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name=b'language name (english)')),
                ('local_name', models.CharField(max_length=200, verbose_name=b'language name (in language)')),
                ('short_code', models.CharField(max_length=5, verbose_name=b"shortcode (e.g. 'en')")),
                ('locale', models.CharField(max_length=5, verbose_name=b"locale (e.g. 'en-us')")),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='content',
            name='grammar_ref',
            field=models.ForeignKey(verbose_name=b'corresponding grammar reference', to='app.Grammar'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='content',
            name='source_lang',
            field=models.ForeignKey(related_name=b'content_written_in', to='app.Language'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='content',
            name='target_lang',
            field=models.ForeignKey(related_name=b'content_written_about', to='app.Language'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='appuser',
            name='lang_learning',
            field=models.ForeignKey(related_name=b'learning', to='app.Language', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='appuser',
            name='lang_speaking',
            field=models.ForeignKey(related_name=b'speaking', to='app.Language', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='appuser',
            name='user_permissions',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions'),
            preserve_default=True,
        ),
    ]
