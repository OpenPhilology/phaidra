from django.db import models

from core.models.sentence import Sentence
from core.models.document import Document

class Word(models.Model):
	CTS = models.CharField(max_length=200)
	value = models.CharField(max_length=100)
	sentence = models.ForeignKey(Sentence)
	document = models.ForeignKey(Document)

	# Morphological information -- not all fields apply to every word
	lemma = models.CharField(max_length=100)
	pos = models.CharField(max_length=10)
	gender = models.CharField(max_length=10, blank=True, null=True)
	case = models.CharField(max_length=10, blank=True, null=True)
	number = models.IntegerField(blank=True, null=True)
	person = models.IntegerField(blank=True, null=True)
	mood = models.CharField(max_length=10, blank=True, null=True)
	tense = models.CharField(max_length=10, blank=True, null=True)
	voice = models.CharField(max_length=10, blank=True, null=True)
