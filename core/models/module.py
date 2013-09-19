from django.db import models

class Module(models.Model):
	uid = models.IntegerField(default=0)

	lesson = models.ForeignKey(Lesson)
