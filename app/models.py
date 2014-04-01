from neo4django.db import models
from neo4django.db.models.manager import NodeModelManager
from neo4django.graph_auth.models import User, UserManager

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.db import models as django_models 

from django.utils import timezone
from datetime import datetime

class AppUser(User):
	
	objects = UserManager()
	
	lang = models.StringProperty(max_length=200)
	
	section = models.IntegerProperty()
	lesson = models.IntegerProperty()
	
	def property_names(self):
		return ['first_name', 'last_name', 'username', 'email', 'is_staff']

	def __unicode__(self):
		return unicode(self.username) or u''

class Document(models.NodeModel):
	# introduced to get API filed work
	internal = models.StringProperty(max_length=200)
	name_eng = models.StringProperty(max_length=200)
	CTS = models.StringProperty(max_length=200)	
	author = models.StringProperty(max_length=200)
	name = models.StringProperty(max_length=200)
	lang = models.StringProperty(max_length = 30)

	def __unicode__(self):
		return unicode(self.name) or u''

class Sentence(models.NodeModel):
	# introduced to get API filed work
	internal = models.StringProperty(max_length=200)
	CTS = models.StringProperty(max_length=200)
	sentence = models.StringProperty()
	length = models.IntegerProperty()
	document = models.Relationship(Document,
                                rel_type='belongs_to',
                                single=True,
                                related_name='sentences'
				#preserve_ordering=True
                               )
	
	def word_objects(self):
		array = []
		for obj in reversed(self.words.all()):
			array.append(obj)
		return array
	
	def get_shortened(self, params = None):
		
		words = self.words.all()
		critique_words = self.words.filter(**params)
		
		# save words within a map for faster lookup		
		dataMap = dict((word.tbwid, word) for word in words)		
		#build tree structure
		dataTree = {0:'root','children':[]}
		for word in words:
			if word.head is 0:					
				dataTree['children'].append(word)			
			else:
				head = dataMap[word.head]
				if head is not None:
						if head.children is not None:
							head.children.append(word)
						else:
							head.children = []
				else:
					dataTree.append(word)
									
		# start here 
		for verb in words:
						
			# if no greek return None
			if verb.relation is None or verb.relation == "":
				return None
			
			# get the verb
			if verb.relation == "PRED" or verb.relation == "PRED_CO":
				s, r, u, i, f, z, g, a = [], [], [], [], [], [], [], []
				aim_words = []
				aim_words2 = []
				aim_words3 = []
				# group the words and make sure, save the selected words
				for word in verb.children:
					if word.relation != "AuxC" and word.relation != "COORD" and word.pos != "participle":
						r.append(word.tbwid)
						aim_words.append(word)
						for w in word.children:
							if w.head in r and w.relation == "ATR" and w.pos != "verb":
								g.append(w.tbwid)
								aim_words.append(w)
						
					if word.relation == "COORD":
						u.append(word.tbwid)
						#aim_words.append(word)
						for w in word.children:
							if w.head in u and (w.relation == "OBJ_CO" or w.relation == "ADV_CO") and w.pos != "participle" and w.pos != "verb":
								i.append(w.tbwid)
								aim_words.append(w)
					
					if word.relation == "AuxP":
						f.append(word.tbwid)
						aim_words.append(word)
						for w in word.children:
							if w.head in f and w.relation != "AuxC" and w.pos != "participle":
								z.append(w.tbwid)
								aim_words.append(w)
					
								for w2 in w.children:
									if w2.head in z and w2.relation == "ATR" and w2.pos != "verb":
										a.append(w2.id)
										aim_words.append(w2)
					
				# refinement of u
				for id in u:
					for id2 in i:
						w = self.words.get(tbwid = id2)
						if w.head is id:
							aim_words.append(w)   
						
				aim_words.append(verb)
				#aim_words = aim_words + aim_words2 + aim_words3
				
				# check if aim_words and critiques match asap
				# check if not verbs only are returned
				# set and order words
				aim_words = set(aim_words)
				if len(list(aim_words & set(critique_words))) > 0 and len(aim_words) > 1:
					return sorted(aim_words, key=lambda x: x.tbwid, reverse=False)
						
		
		return None 
	

	# best this would be created while writing the backend not on calling the method
	def __unicode__(self):
		#words = ""
		#for obj in reversed(self.words.all()):
			#words+= obj.value + " "
		#return str(unicode(words)) or u''
		return unicode(self.sentence) or u''

class Slide(models.NodeModel):
	# Template refers to a front-end template
	# These are used to ultimately render the slide
	title = models.StringProperty()
	template = models.URLProperty()

	# Either a template or an exercize side_type is provided, not both.
	# Exercises are interactive, whereas templates are information only.
	exercise = models.StringProperty()

	# Options is an array of possible solutions to this slide.
	# It is only applicable to slides that require feedback
	options = models.ArrayProperty()

	# Used to compare user-submitted answers to acceptable answers
	answers = models.ArrayProperty()

	# Determines the type of comparisons the system makes between
	# user-submitted answers and accepted answers
	require_all_answers = models.BooleanProperty()
	require_order = models.BooleanProperty()

	def __unicode__(self):
		return str(self.pk)

class SubmissionManager(NodeModelManager):
	
	# catch None attributes of a submission and wrong date formats
	# call the super method "create"
	def create(self, **kwargs):
		if None in kwargs.values() :
			raise ValidationError("Submission attribute is empty. %s" %kwargs.values())
		try:
			date = isinstance(datetime.strptime(kwargs["timestamp"], "%Y-%m-%dT%H:%M:%S"), datetime)
			#date = isinstance(datetime.strptime(kwargs["finished"], "%Y-%m-%dT%H:%M:%S"), datetime)
			kwargs["timestamp"] = datetime.strptime(kwargs["timestamp"], "%Y-%m-%dT%H:%M:%S")
			#kwargs["finished"] = datetime.strptime(kwargs["finished"], "%Y-%m-%dT%H:%M:%S")
		except:
			raise ValidationError('Submission attribute could not be instantiated.')
		return super(SubmissionManager, self).create(**kwargs)


class Submission(models.NodeModel):

	objects = SubmissionManager()

	# the actual user answer
	response = models.ArrayProperty()
	# also contains some of Giuseppes mappings to morph specifiactions
	tasktags = models.ArrayProperty()

	# Set by the client, allows us to determine how must time the user spent
	# on a particular slide.
	speed = models.IntegerProperty()
	# Set by the client. Scale from 1-100 of accuracy. Necessary for exercises that aren't strictly binary questions.
	accuracy = models.IntegerProperty()
	
	# maybe an array of CTS references?! URL array?!
	encounteredWords = models.ArrayProperty()
	# static or dynamic (direct_select, multi_comp, tree) 
	slideType = models.StringProperty()
	
	
	timestamp = models.DateTimeProperty()
	#finished = models.DateTimeProperty()

	user = models.Relationship(AppUser,
		rel_type='answered_by',
		single=True,
		related_name='submissions'
	)

	#slide = models.Relationship(Slide,
	#	rel_type='response_to',
	#	single=True,
	#	related_name='submissions'
	#)

	class Meta:
		app_label = 'models'

	def __unicode__(self):
		return unicode(self.value) or u''	

class Lemma(models.NodeModel):
	
	value = models.StringProperty(max_length=100)
	
	def __unicode__(self):
		return unicode(self.value) or u''
	
	"""
	returns the no. of incoming words to a lemma.
	"""
	def valuesCount(self):
		if self.values is not None:
			return len(self.values.all())
		else :
			return None

class Word(models.NodeModel):
	
	children = models.ArrayProperty()
	internal = models.StringProperty(max_length=200)
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
	
	translation = models.Relationship("Word",
                                rel_type='translation_of',
                                related_name='translation'
                               )
	
	lemmas = models.Relationship(Lemma,
                                rel_type='has_base',
                                single=True,
                                related_name='values'
                               )
	
	def __unicode__(self):
		return unicode(self.value) or u''

