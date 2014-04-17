from django.db import models

class Textbook(models.Model):
	name = models.CharField(max_length=200)
	source_lang = models.CharField(max_length=2)
	target_lang = models.CharField(max_length=2)

	def __unicode__(self):
		return self.name

class Unit(models.Model):
	textbook = models.ForeignKey('TextBook')
	name = models.CharField(max_length=200)
	color = models.CharField(max_length=7)
	graphic = models.FileField(upload_to='units')

	def __unicode__(self):
		return self.name


class Lesson(models.Model):
	unit = models.ForeignKey('Unit')
	name = models.CharField(max_length=200)

	def __unicode__(self):
		return self.name


class Slide(models.Model):
	lesson = models.ForeignKey('Lesson')
	name = models.CharField(max_length=200)
	content = models.TextField()
	smyth = models.CharField(max_length=10)
	tasks = models.CharField(max_length=200)

	def __unicode__(self):
		return self.name

