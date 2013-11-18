from neo4django.db import models

from core.models.user import AppUser
from core.models.slide import Slide

class Submission(models.NodeModel):
	
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
