from neo4django.db import models

from core.models.sentence import Sentence

class Word(models.NodeModel):
	
	CTS = models.StringProperty(max_length=200)
	value = models.StringProperty(max_length=100)
	# this is the length of the value
	length = models.IntegerProperty()
	
	# Morphological information -- not all fields apply to every word
	form = models.StringProperty(max_length=100, blank=True, null=True)
	lemma = models.StringProperty(max_length=100, blank=True, null=True)
	pos = models.StringProperty(max_length=12, blank=True, null=True)
	person = models.StringProperty(max_length=3, blank=True, null=True)
	number = models.StringProperty(max_length=10, blank=True, null=True)
	tense = models.StringProperty(max_length=10, blank=True, null=True)
	mood = models.StringProperty(max_length=10, blank=True, null=True)
	voice = models.StringProperty(max_length=10, blank=True, null=True)
	gender = models.StringProperty(max_length=10, blank=True, null=True)
	case = models.StringProperty(max_length=10, blank=True, null=True)
	degree = models.StringProperty(max_length=10, blank=True, null=True)
	
	# Treebank information -- come from manual annotated sources
	cid = models.IntegerProperty(blank=True, null=True)
	head = models.IntegerProperty(blank=True, null=True)
	tbwid = models.IntegerProperty(blank=True, null=True)
	relation = models.StringProperty(max_length=30, blank=True, null=True)	

	# Morpheus information -- come from work in progress tool
	posClass = models.StringProperty(max_length=1, blank=True, null=True)	
	dialect = models.StringProperty(max_length=100, blank=True, null=True)
	isIndecl = models.StringProperty(max_length=100, blank=True, null=True)
	posAdd = models.StringProperty(max_length=100, blank=True, null=True)
		# Morpheus referencing schema	
	ref = models.StringProperty(max_length=100, blank=True, null=True)

	sentence = models.Relationship(Sentence,
                                rel_type='belongs_to',
                                single=True,
                                related_name='words'
                               )
	
	

	
