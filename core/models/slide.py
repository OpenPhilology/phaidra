from django.db import models

from core.models.custom_fields import SeparatedValuesField
from core.models.module import Module
from core.models.lesson import Lesson

class Slide(models.Model):
	name = models.CharField(max_length=200)
	uid = models.IntegerField(default=0)
	module = models.ForeignKey(Module)
	lesson = models.ForeignKey(Lesson)

	content = models.CharField(max_length=2000)
	options = SeparatedValuesField()
	answers = SeparatedValuesField()

	require_all_answers = models.BooleanField(default=True)
	require_order = models.BooleanField(default=False)

	# User-related metadata
	response = models.CharField(max_length=50)
	speed = models.IntegerField(default=0) # In seconds
	accuracy_degree = models.IntegerField(default=0)
	timestamp = models.DateTimeField() # UTC
