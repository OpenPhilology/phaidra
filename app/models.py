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

	def property_names(self):
		return ['first_name', 'last_name', 'username', 'email', 'is_staff']

	def __unicode__(self):
		return unicode(self.username) or u''

class Document(models.NodeModel):
	CTS = models.StringProperty(max_length=200)	
	author = models.StringProperty(max_length=200)
	name = models.StringProperty(max_length=200)
	lang = models.StringProperty(max_length = 30)

	def __unicode__(self):
		return unicode(self.name) or u''

class Sentence(models.NodeModel):
	CTS = models.StringProperty(max_length=200)
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

	# best this would be created while writing the backend not on calling the method
	def __unicode__(self):
		words = ""
		for obj in reversed(self.words.all()):
			words+= obj.value + " "
		return str(unicode(words)) or u''

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

	class Meta:
		app_label = 'models'

	def __unicode__(self):
		return unicode(self.value) or u''	


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
	
	def __unicode__(self):
		return self.value
