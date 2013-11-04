from django.contrib.auth import authenticate

from neo4django.db import models
from neo4django.graph_auth.models import User
from django.template.defaultfilters import slugify

class User(models.NodeModel):
	username = models.StringProperty(indexed=True)
	email = models.StringProperty()

	def __unicode__(self):
		return unicode(self.username)
	
	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.username)[:50]

		return super(User, self).save(*args, **kwargs)
