from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.safestring import SafeString
from django.template.defaultfilters import truncatechars

class Language(models.Model):
	DIRECTION_CHOICES = (
		('ltr', 'Left-to-right'),
		('rtl', 'Right-to-left')
	)
	name = models.CharField("language name (english)", max_length=200, help_text='(e.g. German)')
	local_name = models.CharField("language name", max_length=200, help_text='(e.g. Deutsch)')
	locale = models.CharField("language code", max_length=5, help_text='(e.g. de-at)')
	short_code = models.CharField("shortcode", max_length=5, help_text='(e.g. \'de\')')
	direction = models.CharField('text direction', choices=DIRECTION_CHOICES, max_length=3)

	def __unicode__(self):
		return unicode(self.name) or u''

class Category(models.Model):
	name = models.CharField('category name', max_length=200)
	graphic = models.CharField(max_length=200, help_text='Image within /static/images/ that should be shown on lesson tiles within this category.', null=True)

	class Meta:
		verbose_name_plural = 'categories'

	def __unicode__(self):
		return unicode(self.name) or u''

class AppUser(AbstractUser):
	objects = UserManager()
	lang_learning = models.ForeignKey(Language, verbose_name='Learning Language', related_name='learning', null=True, help_text='Language the user is learning.')
	lang_speaking = models.ForeignKey(Language, verbose_name='Speaks Language', related_name='speaking', null=True, help_text='Language the user speaks.') 
	
	def __unicode__(self):
		return unicode(self.username) or u''

class Aspect(models.Model):
	ASPECT_CHOICES = (
		('V', 'Vocabulary'),
		('S', 'Syntax'),
		('M', 'Morphology')
	)
	name = models.CharField('aspect name', choices=ASPECT_CHOICES, max_length=1, help_text='')

	def __unicode__(self):
		return unicode(self.get_name_display()) or u''

class Task(models.Model):
	ENDPOINT_CHOICES = (
		('word', 'word'),
		('sentence', 'sentence'),
		('document', 'document')
	)
	name = models.CharField('task name', max_length=100, help_text='Should correspond to something in <a href="https://github.com/OpenPhilology/phaidra/tree/master/static/js/views/lessons/tasks" target="_blank">this folder on Github</a>.')
	endpoint = models.CharField('API endpoint', max_length=20, choices=ENDPOINT_CHOICES, help_text='Defines the API endpoint to which the morphological query should be appended.')
	aspect = models.ManyToManyField(Aspect, verbose_name='knowledge aspect', help_text='Which aspect(s) of this user\'s knowledge is tested?')
	success_msg = models.CharField('success message', max_length=200, help_text='Message the user sees on success.', null=True, blank=True)
	hint_msg = models.CharField('hint message', max_length=200, help_text='Message the user sees on their first incorrect attempt.', null=True, blank=True)

	def __unicode__(self):
		return unicode(self.name) or u''

class TaskSequence(models.Model):
	tasks = models.ManyToManyField(Task, through='TaskContext')
	name = models.CharField('task sequence name', max_length=200, help_text='Name of this unique set and order of tasks. (e.g. "Beginner Nouns" or "Learn to Read Greek")')

	def all_tasks(self):
		return SafeString(', '.join([t.name for t in self.tasks.all()])) 

	def __unicode__(self):
		return unicode(self.name) or u''

class TaskContext(models.Model):
	task_sequence = models.ForeignKey(TaskSequence, verbose_name='task sequence', help_text='The task sequence to which task, with this metadata, belongs.')
	task = models.ForeignKey(Task, verbose_name='task', help_text='Task that belongs in the sequence at this point.')
	target_accuracy = models.FloatField('target accuracy', help_text='Decimal between 0 and 1. When a user reaches this level of accuracy, they move to the next task.')
	max_attempts = models.IntegerField('maximum attempts', help_text='Maximum number of times user should be presented with this task before moving on to the next.')
	order = models.IntegerField(help_text='Order of this task in the defined sequence.')

class Grammar(models.Model):
	ref = models.CharField("Reference", max_length=10, unique=True, help_text="Refers to the section of the grammar book you're using.")
	external_link = models.CharField("external url", max_length=200, null=True, blank=True, help_text='Link to section in the grammar book itself.')
	query = models.CharField("query string", max_length=200, null=True, blank=True, help_text='Describe the morphology of words that fit this grammar topic.')
	title = models.CharField("title of grammar section", max_length=200, help_text='Short, descriptive title of the grammar concept.')
	category = models.ForeignKey(Category, null=True, blank=True)
	tasks = models.ForeignKey(TaskSequence, verbose_name='task sequence', null=True, blank=True)

	class Meta:
		verbose_name = 'Grammar Topic'
		ordering = ['title']

	def __unicode__(self):
		return unicode(self.title) or u''

class Content(models.Model):
	title = models.CharField("title", max_length=200, help_text='Short, descriptive title of what content is in this section.')
	grammar_ref = models.OneToOneField(Grammar, verbose_name="grammar topic", null=True, blank=True, help_text='The morphology directly described by this content.')
	related_topics = models.ManyToManyField(Grammar, verbose_name='related grammar topics', null=True, blank=True, related_name='Topics that would help someone answer questions about this topic (e.g. "Intro to Verbs" is related to "The Aorist Tense").')
	source_lang = models.ForeignKey(Language, related_name='content_written_in', help_text='Language the content is written in.')
	target_lang = models.ForeignKey(Language, related_name='content_written_about', help_text='Language the content teaches.')
	content = models.TextField("Learning Content", help_text='Write this in <a href="https://github.com/OpenPhilology/phaidra/wiki/Phaidra-flavored-Markdown" target="_blank">Phaidra-flavored Markdown</a>.')

	@property
	def content_preview(self):
		return truncatechars(self.content, 90);

	def all_related_topics(self):
		return SafeString('<br>'.join([t.title for t in self.related_topics.all()])) 

	def __unicode__(self):
		return unicode(self.title) or u''
