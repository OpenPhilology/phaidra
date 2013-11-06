from neo4django.db import models

from core.models.user import AppUser
from core.models.slide import Slide

class Submission(models.NodeModel):
	
	value = models.ArrayProperty()
	started = models.DateTimeProperty()
	finished = models.DateTimeProperty()

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
