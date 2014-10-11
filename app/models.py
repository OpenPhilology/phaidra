from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.safestring import SafeString
from django.template.defaultfilters import truncatechars

class Language(models.Model):
	name = models.CharField("language name (english)", max_length=200, help_text='(e.g. German)')
	local_name = models.CharField("language name", max_length=200, help_text='(e.g. Deutsch)')
	locale = models.CharField("language code", max_length=5, help_text='(e.g. de-at)')
	short_code = models.CharField("shortcode", max_length=5, help_text='(e.g. \'de\')')

	def __unicode__(self):
		return unicode(self.name) or u''

class Category(models.Model):
	name = models.CharField(max_length=200)

	class Meta:
		verbose_name_plural = 'categories'

	def __unicode__(self):
		return unicode(self.name) or u''

class AppUser(AbstractUser):
	objects = UserManager()
	lang_learning = models.ForeignKey(Language, related_name='learning', null=True)
	lang_speaking = models.ForeignKey(Language, related_name='speaking', null=True) 
	
	def __unicode__(self):
		return unicode(self.username) or u''

class Grammar(models.Model):
	ref = models.CharField("Reference", max_length=10, unique=True, help_text="Refers to the section of the grammar book you're using.")
	external_link = models.CharField("external url", max_length=200, null=True, blank=True, help_text='Link to section in the grammar book itself')
	query = models.CharField("query string", max_length=200, null=True, blank=True, help_text='Describe the morphology of words that fit this grammar topic')
	title = models.CharField("title of grammar section", max_length=200, help_text='Short, descriptive title of the grammar concept.')
	category = models.ForeignKey(Category)

	class Meta:
		ordering = ['title']

	def __unicode__(self):
		return unicode(self.title) or u''

class Content(models.Model):
	title = models.CharField("title", max_length=200, help_text='Short, descriptive title of what content is in this section')
	grammar_ref = models.OneToOneField(Grammar, verbose_name="grammar topic", null=True, blank=True, help_text='The morphology directly described by this content.')
	related_topics = models.ManyToManyField(Grammar, verbose_name='related grammar topics', null=True, blank=True, related_name='Topics that would help someone answer questions about this topic (e.g. "Intro to Verbs" is related to "The Aorist Tense").')
	source_lang = models.ForeignKey(Language, related_name='content_written_in', help_text='Language the content is written in')
	target_lang = models.ForeignKey(Language, related_name='content_written_about', help_text='Language the content is teaching')
	content = models.TextField("Learning Content", help_text='Write this in <a href="https://github.com/OpenPhilology/phaidra/wiki/Phaidra-flavored-Markdown" target="_blank">Phaidra-flavored Markdown</a>.')

	@property
	def content_preview(self):
		return truncatechars(self.content, 90);

	def all_related_topics(self):
		return SafeString('<br>'.join([t.title for t in self.related_topics.all()])) 

	def __unicode__(self):
		return unicode(self.title) or u''

