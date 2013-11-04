from neo4django.db import models

from core.models.document import Document

class Sentence(models.NodeModel):
	
	CTS = models.StringProperty(max_length=200)
	length = models.IntegerProperty()
	document = models.Relationship(Document,
                                rel_type='belongs_to',
                                single=True,
                                related_name='sentences'
                               )
	def __unicode__(self):
		return unicode(self.CTS) or u''
