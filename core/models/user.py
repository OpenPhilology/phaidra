from django.contrib.auth import authenticate

from neo4django.db import models
from neo4django.graph_auth.models import User, UserManager
from django.template.defaultfilters import slugify


class AppUser(User):
	objects = UserManager()
	slug = models.SlugField()

	#follows = models.Relationship('self', rel_type='follows', related_name='followed_by')
	
	def __unicode__(self):
           return self.title

	def save(self, *args, **kwargs):
        # For automatic slug generation.
        if not self.slug:
            self.slug = slugify(self.title)[:50]

        return super(Entry, self).save(*args, **kwargs)
