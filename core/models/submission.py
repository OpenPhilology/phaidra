from neo4django.db import models
from neo4django.db.models.manager import NodeModelManager

from core.models.user import AppUser
from core.models.slide import Slide


from django.core.exceptions import ValidationError

from django.utils import timezone
from datetime import datetime
#from time import strptime

class SubmissionManager(NodeModelManager):
	
	# catch None attributes of a submission and wrong date formats
	# call the super method "create"
	def create(self, **kwargs):
		if None in kwargs.values() :
			raise ValidationError('Submission attribute is empty.')
		try:
			date = isinstance(datetime.strptime(kwargs["started"], "%Y-%m-%dT%H:%M:%S"), datetime)
			date = isinstance(datetime.strptime(kwargs["finished"], "%Y-%m-%dT%H:%M:%S"), datetime)
			kwargs["started"] = datetime.strptime(kwargs["started"], "%Y-%m-%dT%H:%M:%S")
			kwargs["finished"] = datetime.strptime(kwargs["finished"], "%Y-%m-%dT%H:%M:%S")
		except:
			raise ValidationError('Submission attribute could not be instantiated.')
		return super(SubmissionManager, self).create(**kwargs)


class Submission(models.NodeModel):

	objects = SubmissionManager()

	value = models.ArrayProperty()

	# Set by the client, allows us to determine how must time the user spent
	# on a particular slide.
	started = models.DateTimeProperty()
	finished = models.DateTimeProperty()

	# Scale from 1-10 of accuracy. Necessary for exercises that aren't strictly
	# binary questions.
	accuracy = models.IntegerProperty()

	user = models.Relationship(AppUser,
		rel_type='answered_by',
		single=True,
		related_name='submissions'
	)

	slide = models.Relationship(Slide,
		rel_type='response_to',
		single=True,
		related_name='submissions'
	)

	def __unicode__(self):
		return unicode(self.value) or u''	

