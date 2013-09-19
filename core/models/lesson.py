from django.db import models

class Lesson(models.Model):
	name = models.CharField(max_length=200)
