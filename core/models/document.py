from django.db import models

class Document(models.Model):
	name = models.CharField(max_length=200)
	CTS = models.CharField(max_length=200)
	author = models.CharField(max_length=200)
	lang = models.charField(max_length = 30)

