from django.db import models

class User(models.Model):
	user = models.CharField(max_length=50)
	email = models.CharField(max_length=200)
