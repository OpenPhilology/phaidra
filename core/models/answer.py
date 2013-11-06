from neo4django.db import models

from core.models.user import AppUser
from core.models.slide import Slide

class Answer(models.NodeModel):
	
	submission = models.ArrayProperty()
	started = models.DateTimeProperty()
	finished = models.DateTimeProperty()

	user = models.Relationship(AppUser,
                                rel_type='answered_by',
                                related_name='answers'
                               )

	slide = models.Relationship(Slide,
                                rel_type='response_to',
                                related_name='answers'
                               )

	def __unicode__(self):
		return unicode(self.submission) or u''
