from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.text import slugify

class AppUser(AbstractUser):
	
	objects = UserManager()
	
	lang = models.CharField(max_length=200)
	unit = models.IntegerField(default=0)
	lesson = models.IntegerField(default=0)
	progress = models.IntegerField(default=0)
	
	def __unicode__(self):
		return unicode(self.username) or u''

class Textbook(models.Model):
	name = models.CharField(max_length=200)
	source_lang = models.CharField(max_length=2)
	target_lang = models.CharField(max_length=2)

	def __unicode__(self):
		return unicode(self.name) or u''

class Unit(models.Model):
	textbook = models.ForeignKey('TextBook')
	name = models.CharField(max_length=200)
	color = models.CharField(max_length=7)
	graphic = models.FileField(upload_to='units', blank=True)
	order = models.IntegerField()

	def __unicode__(self):
		return self.name

class Lesson(models.Model):
	unit = models.ForeignKey('Unit')
	name = models.CharField(max_length=200)
	order = models.IntegerField()

	def __unicode__(self):
		return self.name

class Slide(models.Model):
	lesson = models.ForeignKey('Lesson')
	name = models.CharField(max_length=200)
	content = models.TextField()
	smyth = models.CharField(max_length=10, blank=True)
	task = models.CharField(max_length=200, blank=True)
	order = models.IntegerField()

	def __unicode__(self):
		return self.name

