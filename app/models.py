from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

class Language(models.Model):
	name = models.CharField("language name (english)", max_length=200)
	local_name = models.CharField("language name (in language)", max_length=200)
	short_code = models.CharField("shortcode (e.g. 'en')", max_length=5)
	locale = models.CharField("locale (e.g. 'en-us')", max_length=5)

	def __unicode__(self):
		return unicode(self.name) or u''

class Category(models.Model):
	name = models.CharField(max_length=200)

	def __unicode__(self):
		return unicode(self.name) or u''

class AppUser(AbstractUser):
	
	objects = UserManager()
	
	lang_learning = models.ForeignKey(Language, related_name='learning', null=True)
	lang_speaking = models.ForeignKey(Language, related_name='speaking', null=True) 
	
	def __unicode__(self):
		return unicode(self.username) or u''

class Grammar(models.Model):
	ref = models.CharField("reference to the grammar book section", max_length=10, unique=True)
	external_link = models.CharField("external url for reference lookup", max_length=200, null=True, blank=True)
	query = models.CharField("query string", max_length=200, null=True, blank=True)
	title = models.CharField("title of grammar section", max_length=200)
	category = models.ForeignKey(Category)

	class Meta:
		ordering = ['title']

	def __unicode__(self):
		return unicode(self.title) or u''

class Content(models.Model):
	title = models.CharField("title of contents", max_length=200)
	grammar_ref = models.OneToOneField(Grammar, verbose_name="corresponding grammar reference", null=True, blank=True)
	related_topics = models.ManyToManyField(Grammar, verbose_name='related grammar topics', null=True, blank=True, related_name='relates_to')
	source_lang = models.ForeignKey(Language, related_name='content_written_in')
	target_lang = models.ForeignKey(Language, related_name='content_written_about')
	content = models.TextField("content written in markdown")

	def __unicode__(self):
		return unicode(self.title) or u''

