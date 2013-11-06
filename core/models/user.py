from django.contrib.auth import authenticate

from django.db import models as django_models 
from neo4django.db import models
from neo4django.graph_auth.models import User, UserManager


class AppUser(User):
	objects = UserManager()

	#follows = models.Relationship('self', rel_type='follows', related_name='followed_by')
	
	def __unicode__(self):
           return self.username
