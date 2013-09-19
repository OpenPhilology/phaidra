from django.db import models

from core.models.document import Document

class Sentence(models.Model):
	CTS = models.CharField(max_length=200)
	document = models.ForeignKey(Document)
	length = models.IntegerField()
