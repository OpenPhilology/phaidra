from __future__ import unicode_literals
# coding: utf8
from phaidra import settings
from phaidra.settings import GRAPH_DATABASE_REST_URL, API_PATH

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phaidra.settings")
from django.conf import settings 
from django.conf.urls import url
from app.models import Textbook, Unit, Lesson, Slide, AppUser

from django.core.exceptions import ValidationError

from tastypie import fields
from tastypie.resources import Resource, ModelResource

from neo4jrestclient.client import GraphDatabase
#from neo4jrestclient import client

from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.authentication import SessionAuthentication, BasicAuthentication
from tastypie.authorization import Authorization, ReadOnlyAuthorization
from tastypie.utils import trailing_slash
from tastypie.http import HttpUnauthorized, HttpForbidden, HttpBadRequest
from tastypie.exceptions import NotFound, BadRequest, Unauthorized

import json
import random
from random import shuffle

import time

class UserObjectsOnlyAuthorization(Authorization):
	
	def read_list(self, object_list, bundle):
		
		gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)	
		submissions = []
		table = gdb.query("""START u=node(*) MATCH (u)-[:submissions]->(s) WHERE HAS (u.username) AND u.username='""" + bundle.request.user.username + """' RETURN s""")		
			
		# create the objects which was queried for and set all necessary attributes
		for s in table:
			submission = s[0]	
			url = submission['self'].split('/')						
			new_obj = DataObject(url[len(url)-1])
			new_obj.__dict__['_data'] = submission['data']		
			new_obj.__dict__['_data']['id'] = url[len(url)-1]						
			submissions.append(new_obj)
				
		return submissions
	
	def read_detail(self, object_list, bundle):
		
		if bundle.request.user is not None:
			return object_list				
		else:
			raise Unauthorized()
	
	### not in use yet. User submissions are related to the user in the sent data, which makes sure the the user was already verified
	def create_detail(self, object_list, bundle):
		return bundle.obj.user == bundle.request.user






#db = GraphDatabase('/var/lib/neo4j/data/graph.db/')

class TextbookResource(ModelResource):
	class Meta:
		queryset = Textbook.objects.all()
		resource_name = 'textbook'
		allowed_methods = ['get']

class UnitResource(ModelResource):
	class Meta:
		queryset = Unit.objects.all()
		resource_name = 'unit'
		allowed_methods = ['get']

class LessonResource(ModelResource):
	class Meta:
		queryset = Lesson.objects.all()
		resource_name = 'lesson'
		allowed_methods = ['get']

class SlideResource(ModelResource):
	class Meta:
		queryset = Slide.objects.all()
		resource_name = 'slide'
		allowed_methods = ['get']

class UserResource(ModelResource):
	class Meta:
		queryset = AppUser.objects.all()
		resource_name = 'user'
		fields = ['username', 'first_name', 'last_name', 'last_login']


"""
Simple object for creating the instances.
"""		
class DataObject(object):
	
    def __init__(self, id=None):
    	
    	self.__dict__['_data'] = {}
    	
    	if not hasattr(id, 'id') and id is not None:
    		
    		self.__dict__['_data']['id'] = id
         	
    def __getattr__(self, name):
        return self._data.get(name, None)

    def __setattr__(self, name, value):
        self.__dict__['_data'][name] = value

    def to_dict(self):
        return self._data
     

"""
Derivatives from Resource.
"""		
		
class SubmissionResource(Resource):
	
	response = fields.CharField(attribute='response', null = True, blank = True) 
	task = fields.CharField(attribute='task', null = True, blank = True)
	smyth = fields.CharField(attribute='smyth', null = True, blank = True)
	time = fields.IntegerField(attribute='time', null = True, blank = True)
	accuracy = fields.IntegerField(attribute='accuracy', null = True, blank = True)
	encounteredWords = fields.ListField(attribute='encounteredWords', null = True, blank = True)
	slideType = fields.CharField(attribute='slideType', null = True, blank = True)
	timestamp = fields.DateField(attribute='timestamp', null = True, blank = True)
	
	class Meta:
		allowed_methods = ['post', 'get', 'patch']
		#authentication = SessionAuthentication() 
		authentication = BasicAuthentication()
		authorization = UserObjectsOnlyAuthorization()
		object_class = DataObject
		resource_name = 'submission'

	def detail_uri_kwargs(self, bundle_or_obj):
		
		kwargs = {}	
		if isinstance(bundle_or_obj, Bundle):
			kwargs['pk'] = bundle_or_obj.obj.id	
		else:
			kwargs['pk'] = bundle_or_obj.id		
		return kwargs

	def authorized_read_list(self, object_list, bundle):
		"""
		Handles checking of permissions to see if the user has authorization
		to GET this resource.
		"""
		try:
			auth_result = self._meta.authorization.read_list(object_list, bundle)
		except Unauthorized as e:
			self.unauthorized_result(e)

		return auth_result

	#def get_object_list(self, request):
		
		#gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)	
		#submissions = []
		#table = gdb.query("""START u=node(*) MATCH (u)-[:submissions]->(s) RETURN s""")		
			
		# create the objects which was queried for and set all necessary attributes
		#for s in table:
			#submission = s[0]	
			#url = submission['self'].split('/')						
			#new_obj = DataObject(url[len(url)-1])
			#new_obj.__dict__['_data'] = submission['data']		
			#new_obj.__dict__['_data']['id'] = url[len(url)-1]						
			#submissions.append(new_obj)
				
		#return submissions
	
	def obj_get_list(self, bundle, **kwargs):
		
		try:
			return self.authorized_read_list(bundle.request, bundle)
		except ValueError:
			raise BadRequest("Invalid resource lookup data provided (mismatched type).")
		
		#return self.get_object_list(bundle.request)
	
	def obj_get(self, bundle, **kwargs):
		
		gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)
		submission = gdb.nodes.get(GRAPH_DATABASE_REST_URL + "node/" + kwargs['pk'] + '/')
			
		new_obj = DataObject(kwargs['pk'])
		new_obj.__dict__['_data'] = submission.properties
		new_obj.__dict__['_data']['id'] = kwargs['pk']
			
		try:
			auth_result = self._meta.authorization.read_detail(new_obj, bundle)
		except Unauthorized as e:
			self.unauthorized_result(e)

		return auth_result	
		
	def post_list(self, request, **kwargs):
		"""
		Create a new submission object, which relates to the slide it responds to and the user who submitted it.
		Return the submission object, complete with whether or not they got the answer correct.
		"""
		gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)
		
		self.method_check(request, allowed=['post'])
		#self.is_authenticated(request)

		if not request.user or not request.user.is_authenticated():
			return self.create_response(request, { 'success': False, 'error_message': 'You are not authenticated, %s' % request.user })

		data = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
		# Ensuring that the user is who s/he says s/he is, handled by user objs. auth.
		#try:
			#user_node = AppUser.objects.get(username=data.get("user"))
		#except ObjectDoesNotExist as e:
			#return self.create_response(request, {'success': False, 'error': e})

		# get the user via neo look-up or create a newone
		if data['user'] is not None:
			userTable = gdb.query("""START u=node(*) MATCH (u)-[:submissions]->(s) WHERE HAS (u.username) AND u.username='""" + data['user'] + """' RETURN u""")
		
			if len(userTable) > 0:	
				userurl = userTable[0][0]['self']
				userNode = gdb.nodes.get(userurl)			
			
			else:
				userNode = gdb.node(username=data['user'])
			
			subms = gdb.node(
				response = data.get("response"), # string 
				task = data.get("task"), # string 
				smyth = data.get("smyth"),	# string
				time = int(data.get("time")),		 # integer
				accuracy = int(data.get("accuracy")), # integer
				encounteredWords = data.get("encounteredWords"), # array
				slideType = data.get("slideType"), # string
				timestamp = data.get("timestamp") # datetime
			)
			if subms is None :
				# in case an error wasn't already raised 			
				raise ValidationError('Submission node could not be created.')
		
			# Form the connections from the new Submission node to the existing slide and user nodes
			userNode.submissions(subms)
	
			# create the body
			body = json.loads(request.body) if type(request.body) is str else request.body
	
			return self.create_response(request, body)
		
		else:
			return self.error_response(request, {'error': 'User is required.' }, response_class=HttpBadRequest)

       
"""
Here start the data resources.
"""      

class LemmaResource(Resource):
	
	CITE = fields.CharField(attribute='CITE')
	value = fields.CharField(attribute='value')
	posAdd = fields.CharField(attribute='posAdd', null = True, blank = True)
	frequency = fields.IntegerField(attribute='frequency', null = True, blank = True)
	
	values = fields.ListField(attribute='values', null = True, blank = True)
	
	class Meta:
	
		resource_name = 'lemma'
		object_class = DataObject
		authorization = ReadOnlyAuthorization()
	
	def detail_uri_kwargs(self, bundle_or_obj):
		
		kwargs = {}
		if isinstance(bundle_or_obj, Bundle):
			kwargs['pk'] = bundle_or_obj.obj.id			
		else:
			kwargs['pk'] = bundle_or_obj.id			
		return kwargs
	
	#/api/word/?randomized=&format=json&lemma=κρατέω
	def get_object_list(self, request):
		
		gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)	
		attrlist = ['CITE', 'value', 'posAdd', 'frequency']
		lemmas = []
		
		query_params = {}
		for obj in request.GET.keys():
			if obj in attrlist and request.GET.get(obj) is not None:
				query_params[obj] = request.GET.get(obj)
			elif obj.split('__')[0] in attrlist and request.GET.get(obj) is not None:
				query_params[obj] = request.GET.get(obj)
		
		# implement filtering
		if len(query_params) > 0:
			
			# generate query
			q = """START l=node(*) MATCH (l)-[:values]->(w) WHERE """
			
			# filter word on parameters
			for key in query_params:
				if len(key.split('__')) > 1:
					if key.split('__')[1] == 'contains':
						q = q + """HAS (l.""" +key.split('__')[0]+ """) AND l.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """.*' AND """
					elif key.split('__')[1] == 'startswith':
						q = q + """HAS (l.""" +key.split('__')[0]+ """) AND l.""" +key.split('__')[0]+ """=~'""" +query_params[key]+ """.*' AND """
					elif key.split('__')[1] == 'endswith':
						q = q + """HAS (l.""" +key.split('__')[0]+ """) AND l.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """' AND """
					elif key.split('__')[1] == 'gt':
						q = q + """HAS (l.""" +key.split('__')[0]+ """) AND l.""" +key.split('__')[0]+ """>""" +query_params[key]+ """ AND """
					elif key.split('__')[1] == 'lt':
						q = q + """HAS (l.""" +key.split('__')[0]+ """) AND l.""" +key.split('__')[0]+ """<""" +query_params[key]+ """ AND """
				else:
					if key == 'frequency':
						q = q + """HAS (l.""" +key+ """) AND l.""" +key+ """=""" +query_params[key]+ """ AND """
					else:
						q = q + """HAS (l.""" +key+ """) AND l.""" +key+ """='""" +query_params[key]+ """' AND """
			q = q[:len(q)-4]
			q = q + """RETURN DISTINCT l ORDER BY ID(l)"""
			
			table = gdb.query(q)
		
		# default querying	
		else:	
			table = gdb.query("""START l=node(*) MATCH (l)-[:values]->(w) WHERE HAS (l.CITE) RETURN DISTINCT l ORDER BY ID(l)""")
			
		# create the objects which was queried for and set all necessary attributes
		for t in table:
			lemma = t[0]	
			url = lemma['self'].split('/')		
				
			new_obj = DataObject(url[len(url)-1])
			new_obj.__dict__['_data'] = lemma['data']		
			new_obj.__dict__['_data']['id'] = url[len(url)-1]
			
			# get the word as a node to query relations
			lemmaNode = gdb.nodes.get(lemma['self'])
			
			values = lemmaNode.relationships.outgoing(types=["values"])	
			valuesArray = []
			for v in range(0, len(values), 1):
				val = values[v].end
				val.properties['resource_uri'] = API_PATH + 'word/' + str(val.id) + '/'
				valuesArray.append(val.properties)
				
			new_obj.__dict__['_data']['values'] = valuesArray			
			lemmas.append(new_obj)
				
		return lemmas
	
	def obj_get_list(self, bundle, **kwargs):
		
		return self.get_object_list(bundle.request)
	
	def obj_get(self, bundle, **kwargs):
		
		gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)
		lemma = gdb.nodes.get(GRAPH_DATABASE_REST_URL + "node/" + kwargs['pk'] + '/')
		
		# ge the data of the word
		new_obj = DataObject(kwargs['pk'])
		new_obj.__dict__['_data'] = lemma.properties
		new_obj.__dict__['_data']['id'] = kwargs['pk']
		
		# get the values	
		values = lemma.relationships.outgoing(types=["values"])			
		valuesArray = []
		for v in range(0, len(values), 1):
			val = values[v].end
			val.properties['resource_uri'] = API_PATH + 'word/' + str(val.id) + '/'
			valuesArray.append(val.properties)
			
		new_obj.__dict__['_data']['values'] = valuesArray

		return new_obj

class WordResource(Resource):
	
	CTS = fields.CharField(attribute='CTS')
	value = fields.CharField(attribute='value')
	form = fields.CharField(attribute='form', null = True, blank = True)
	lemma = fields.CharField(attribute='lemma', null = True, blank = True)
	ref = fields.CharField(attribute='ref', null = True, blank = True)
	
	sentence_resource_uri = fields.CharField(attribute='sentence_resource_uri', null = True, blank = True)
	
	length = fields.IntegerField(attribute='length', null = True, blank = True)
	tbwid = fields.IntegerField(attribute='tbwid', null = True, blank = True)
	head = fields.IntegerField(attribute='head', null = True, blank = True)
	cid = fields.IntegerField(attribute='cid', null = True, blank = True)
	
	pos = fields.CharField(attribute='pos', null = True, blank = True)
	person = fields.CharField(attribute='person', null = True, blank = True)
	number = fields.CharField(attribute='number', null = True, blank = True)
	tense = fields.CharField(attribute='tense', null = True, blank = True)
	mood = fields.CharField(attribute='mood', null = True, blank = True)
	voice = fields.CharField(attribute='voice', null = True, blank = True)
	gender = fields.CharField(attribute='gender', null = True, blank = True)
	case = fields.CharField(attribute='case', null = True, blank = True)
	degree = fields.CharField(attribute='degree', null = True, blank = True)
	
	relation = fields.CharField(attribute='relation', null = True, blank = True)	
	
	dialect = fields.CharField(attribute='dialect', null = True, blank = True)
	posClass = fields.CharField(attribute='posClass', null = True, blank = True)
	posAdd = fields.CharField(attribute='posAdd', null = True, blank = True)
	isIndecl = fields.CharField(attribute='isIndecl', null = True, blank = True)
	
	lemma_resource_uri = fields.CharField(attribute='lemma_resource_uri', null = True, blank = True)
	translations = fields.ListField(attribute='translations', null = True, blank = True)
	
	class Meta:
	
		resource_name = 'word'
		object_class = DataObject
		authorization = ReadOnlyAuthorization()
	
	def detail_uri_kwargs(self, bundle_or_obj):
		
		kwargs = {}		
		if isinstance(bundle_or_obj, Bundle):
			kwargs['pk'] = bundle_or_obj.obj.id
		else:
			kwargs['pk'] = bundle_or_obj.id
		return kwargs
	
	#/api/word/?randomized=&format=json&lemma=κρατέω
	def get_object_list(self, request):
		
		gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)	
		attrlist = ['CTS', 'length', 'case', 'dialect', 'head', 'form', 'posClass', 'cid', 'gender', 'tbwid', 'pos', 'value', 'degree', 'number','lemma', 'relation', 'isIndecl', 'ref', 'posAdd', 'mood', 'tense', 'voice', 'person']
		words = []
		
		query_params = {}
		for obj in request.GET.keys():
			if obj in attrlist and request.GET.get(obj) is not None:
				query_params[obj] = request.GET.get(obj)
			elif obj.split('__')[0] in attrlist and request.GET.get(obj) is not None:
				query_params[obj] = request.GET.get(obj)
		
		# implement filtering
		if len(query_params) > 0:
			
			# generate query
			q = """START s=node(*) MATCH (s)-[:words]->(w) WHERE """
			
			# filter word on parameters
			for key in query_params:
				if len(key.split('__')) > 1:
					if key.split('__')[1] == 'contains':
						q = q + """HAS (w.""" +key.split('__')[0]+ """) AND w.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """.*' AND """
					elif key.split('__')[1] == 'startswith':
						q = q + """HAS (w.""" +key.split('__')[0]+ """) AND w.""" +key.split('__')[0]+ """=~'""" +query_params[key]+ """.*' AND """
					elif key.split('__')[1] == 'endswith':
						q = q + """HAS (w.""" +key.split('__')[0]+ """) AND w.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """' AND """
				else:
					q = q + """HAS (w.""" +key+ """) AND w.""" +key+ """='""" +query_params[key]+ """' AND """
			q = q[:len(q)-4]
			q = q + """RETURN w, s ORDER BY ID(w)"""
			
			table = gdb.query(q)
		
		# default querying	
		else:	
			table = gdb.query("""START s=node(*) MATCH (s)-[:words]->(w) WHERE HAS (w.CTS) RETURN w, s ORDER BY ID(w)""")
			
		# create the objects which was queried for and set all necessary attributes
		for t in table:
			word = t[0]
			sentence = t[1]		
			url = word['self'].split('/')
			urlSent = sentence['self'].split('/')		
				
			new_obj = DataObject(url[len(url)-1])
			new_obj.__dict__['_data'] = word['data']		
			new_obj.__dict__['_data']['id'] = url[len(url)-1]
			new_obj.__dict__['_data']['sentence_resource_uri'] = API_PATH + 'sentence/' + urlSent[len(urlSent)-1] +'/'
			
			# get the word as a node to query relations
			#wordNode = gdb.nodes.get(word['self'])
			
			# get the lemma -> too expensive here, put it into detail view			
			#lemmaRels = word.relationships.incoming(types=["values"])
			#if len(lemmaRels) > 0:
				#new_obj.__dict__['_data']['lemma_resource'] = API_PATH + 'lemma/' + str(lemmaRels[0].start.id) + '/'
			
			# get the translations -> too expensive here, put in into detail view	
			#translations = wordNode.relationships.outgoing(types=["translation"])	
			#translationArray = []
			#for t in translations:
				#trans = t.end
				#trans.properties['resource_uri'] = API_PATH + 'word/' + str(trans.id) + '/'
				#translationArray.append(trans.properties)
				
			#new_obj.__dict__['_data']['translations'] = reversed(translationArray)			
			words.append(new_obj)
				
		return words
	
	def obj_get_list(self, bundle, **kwargs):
		
		return self.get_object_list(bundle.request)
	
	def obj_get(self, bundle, **kwargs):
		
		gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)
		word = gdb.nodes.get(GRAPH_DATABASE_REST_URL + "node/" + kwargs['pk'] + '/')
		
		# ge the data of the word
		new_obj = DataObject(kwargs['pk'])
		new_obj.__dict__['_data'] = word.properties
		new_obj.__dict__['_data']['id'] = kwargs['pk']
		new_obj.__dict__['_data']['sentence_resource_uri'] = API_PATH + 'sentence/' + str(word.relationships.incoming(types=["words"])[0].start.id) + '/'
		
		# get the lemma
		lemmaRels = word.relationships.incoming(types=["values"])
		if len(lemmaRels) > 0:
			new_obj.__dict__['_data']['lemma_resource_uri'] = API_PATH + 'lemma/' + str(lemmaRels[0].start.id) + '/'
		
		# get the translations	
		translations = word.relationships.outgoing(types=["translation"])			
		translationArray = []
		for t in range(0, len(translations), 1):
			trans = translations[t].end
			trans.properties['resource_uri'] = API_PATH + 'word/' + str(trans.id) + '/'
			translationArray.append(trans.properties)
			
		new_obj.__dict__['_data']['translations'] = translationArray

		return new_obj

class SentenceResource(Resource):
	
	CTS = fields.CharField(attribute='CTS', null = True, blank = True)
	sentence = fields.CharField(attribute='sentence', null = True, blank = True)	
	length = fields.IntegerField(attribute='length', null = True, blank = True)
	document_resource_uri = fields.CharField(attribute='document_resource_uri', null = True, blank = True)
	words = fields.ListField(attribute='words', null = True, blank = True)
	translations = fields.DictField(attribute='translations', null = True, blank = True)
	
	class Meta:
		
		resource_name = 'sentence'
		object_class = DataObject
		authorization = ReadOnlyAuthorization()	
	
	def detail_uri_kwargs(self, bundle_or_obj):
		
		kwargs = {}
		if isinstance(bundle_or_obj, Bundle):
			kwargs['pk'] = bundle_or_obj.obj.id	
		else:
			kwargs['pk'] = bundle_or_obj.id	
		return kwargs


	def get_object_list(self, request):
		
		gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)	
		attrlist = ['CTS', 'length', 'sentence']
		sentences = []
		
		query_params = {}
		for obj in request.GET.keys():
			if obj in attrlist and request.GET.get(obj) is not None:
				query_params[obj] = request.GET.get(obj)
			elif obj.split('__')[0] in attrlist and request.GET.get(obj) is not None:
				query_params[obj] = request.GET.get(obj)
		
		# implement filtering
		if len(query_params) > 0:
			
			# generate query
			q = """START d=node(*) MATCH (d)-[:sentences]->(s) WHERE """
			
			# filter word on parameters
			for key in query_params:
				if len(key.split('__')) > 1:
					if key.split('__')[1] == 'contains':
						q = q + """HAS (s.""" +key.split('__')[0]+ """) AND s.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """.*' AND """
					elif key.split('__')[1] == 'startswith':
						q = q + """HAS (s.""" +key.split('__')[0]+ """) AND s.""" +key.split('__')[0]+ """=~'""" +query_params[key]+ """.*' AND """
					elif key.split('__')[1] == 'endswith':
						q = q + """HAS (s.""" +key.split('__')[0]+ """) AND s.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """' AND """
				else:
					q = q + """HAS (s.""" +key+ """) AND s.""" +key+ """='""" +query_params[key]+ """' AND """
			q = q[:len(q)-4]
			q = q + """RETURN s, d ORDER BY ID(s)"""
			
			table = gdb.query(q)
		
		# default querying	
		else:	
			table = gdb.query("""START d=node(*) MATCH (d)-[:sentences]->(s) WHERE HAS (s.CTS) RETURN s, d ORDER BY ID(s)""")
			
		# create the objects which was queried for and set all necessary attributes
		for t in table:
			sentence = t[0]
			document = t[1]		
			url = sentence['self'].split('/')
			urlDoc = document['self'].split('/')		
				
			new_obj = DataObject(url[len(url)-1])
			new_obj.__dict__['_data'] = sentence['data']		
			new_obj.__dict__['_data']['id'] = url[len(url)-1]
			new_obj.__dict__['_data']['document_resource_uri'] = API_PATH + 'document/' + urlDoc[len(urlDoc)-1] +'/'
			sentences.append(new_obj)
				
		return sentences
	
	def obj_get_list(self, bundle, **kwargs):
		
		return self.get_object_list(bundle.request)
	
	def obj_get(self, bundle, **kwargs):
		
		# query parameters (optional) for short sentence approach
		attrlist = ['CTS', 'length', 'case', 'dialect', 'head', 'form', 'posClass', 'cid', 'gender', 'tbwid', 'pos', 'value', 'degree', 'number','lemma', 'relation', 'isIndecl', 'ref', 'posAdd', 'mood', 'tense', 'voice', 'person']
		query_params = {}
		for obj in bundle.request.GET.keys():
			if obj in attrlist and bundle.request.GET.get(obj) is not None:
				query_params[obj] = bundle.request.GET.get(obj)
			elif obj.split('__')[0] in attrlist and bundle.request.GET.get(obj) is not None:
				query_params[obj] = bundle.request.GET.get(obj)
		
		gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)
		sentence = gdb.nodes.get(GRAPH_DATABASE_REST_URL + "node/" + kwargs['pk'] + '/')
			
		# get the sentence parameters			
		new_obj = DataObject(kwargs['pk'])
		new_obj.__dict__['_data'] = sentence.properties
		new_obj.__dict__['_data']['id'] = kwargs['pk']
		new_obj.__dict__['_data']['document_resource_uri'] = API_PATH + 'document/' + str(sentence.relationships.incoming(types=["sentences"])[0].start.id) + '/'
		
		# get a dictionary or related translation of this sentence # ordering here is a problem child
		relatedSentences = gdb.query("""START s=node(*) MATCH (s)-[:words]->(w)-[:translation]->(t)<-[:words]-(s1) WHERE HAS (s.CTS) AND s.CTS='""" 
						+ sentence.properties['CTS'] + """' RETURN DISTINCT s1 ORDER BY ID(s1)""")
		
		new_obj.__dict__['_data']['translations']={}
		for rs in relatedSentences:
			sent = rs[0]
			url = sent['self'].split('/')
			cts_outtake = sent['data']['CTS'].split(':')[len(sent['data']['CTS'].split(':'))-2]
			key = cts_outtake.split('-')[len(cts_outtake.split('-'))-1]
			new_obj.__dict__['_data']['translations'][key] = API_PATH + 'sentence/' + url[len(url)-1] +'/'		
						
		# get the words
		words = sentence.relationships.outgoing(types=["words"])
		wordArray = []		
		for w in range(0, len(words), 1):
			word = words[w].end
			# get the lemma of a word
			lemmaRels = word.relationships.incoming(types=["values"])
			if len(lemmaRels) > 0:
				word.properties['lemma_resource_uri'] = API_PATH + 'lemma/' + str(lemmaRels[0].start.id) + '/'
		
			# create the resource uri of the word
			word.properties['resource_uri'] = API_PATH + 'word/' + str(word.id) + '/'		
			
			# if full=True return also the translation data to the words
			if bundle.request.GET.get('full'):
				translationRels = word.relationships.outgoing(types=["translation"])
				translationArray = []
				#for t in translationRels:
				for i in range(0, len(translationRels), 1):
					trans = translationRels[i].end
					#trans = t.end
					trans.properties['resource_uri'] = API_PATH + 'word/' + str(trans.id) + '/'
					translationArray.append(trans.properties)

				word.properties['translations'] = translationArray
			
			wordArray.append(word.properties)
		
		# if short=True return only words of the short sentence
		if bundle.request.GET.get('short'):
			wordArray =  self.shorten(wordArray, query_params)
			if wordArray is None:
				#return None
				raise BadRequest("Sentence doesn't hit your query.")		
				#return self.error_response(bundle.request, {'error': ''}, response_class=HttpBadRequest)	
						
		new_obj.__dict__['_data']['words'] = wordArray
			
		return new_obj
	
	
	class node(object):
		
		def __init__(self, value):
			self.value = value
			self.children = []
			
		def add_child(self, obj):
			self.children.append(obj)
					
	"""
	Function for shortening a sentence
	"""	
	def shorten(self, wordArray, params = None):
		
		words = wordArray		
		# interrupt as soon as possible if there is no according syntactical information available
		try:
			words[0]['head']
		except KeyError as k:
			return None
			
		# save words within a map for faster lookup			
		nodes = dict((word['tbwid'], self.node(word)) for word in words)
		# build a "tree"
		verbs = []
		for w in words:
			if w['head'] is not 0:
	   			nodes[w['head']].add_child(nodes[w['tbwid']])
	   		if w['relation'] == "PRED" or w['relation'] == "PRED_CO":
	   			verbs.append(w)
														
		# start here 
		for verb in verbs:					
			# get the verb
			if verb['relation'] == "PRED" or verb['relation'] == "PRED_CO":						
				u, i = [], []
				aim_words = []
				# group the words and make sure, save the selected words
				for word in nodes[verb['tbwid']].children:
											
					if word.value['relation'] == "COORD":
						u.append(word.value['tbwid'])
						#aim_words.append(word)
						for w in nodes[word.value['tbwid']].children:
							if (w.value['relation'] == "OBJ_CO" or w.value['relation'] == "ADV_CO") and w.value['pos'] != "participle" and w.value['pos'] != "verb":
								i.append(w.value['tbwid'])
								aim_words.append(w.value)
					
					elif word.value['relation'] == "AuxP":
						aim_words.append(word.value)
						for w in nodes[word.value['tbwid']].children:
							if w.value['relation'] != "AuxC" and w.value['pos'] != "participle":
								aim_words.append(w.value)
					
								for w2 in nodes[w.value['tbwid']].children:
									if w2.value['relation'] == "ATR" and w2.value['pos'] != "verb":
										aim_words.append(w2.value)
										
										
					elif word.value['relation'] != "AuxC" and word.value['relation'] != "COORD" and word.value['pos'] != "participle":
						aim_words.append(word.value)
						for w in nodes[word.value['tbwid']].children:
							if w.value['relation'] == "ATR" and w.value['pos'] != "verb":
								aim_words.append(w.value)
					
				# refinement of u
				for id in u:
					for id2 in i:
						w = nodes[id2].value
						if w['head'] is id:
							aim_words.append(w)   
							
				aim_words.append(verb)
					
				# check if not verbs only are returned
				if len(aim_words) > 1:
					# consider params
					if len(params) > 0:
						# check if aim_words and parameter filtered intersect 
						cand = False
						for w in aim_words:
							for key in params:
								if w[key] == params[key]:
									cand = True
								else:
									cand = False
									continue
							
							if cand:										
								# set and order words
								return sorted(aim_words, key=lambda x: x['tbwid'], reverse=True)	
						
						return None		
					else:		
						# set and order words
						return sorted(aim_words, key=lambda x: x['tbwid'], reverse=True)				
					
					# set and order words
					return sorted(aim_words, key=lambda x: x['tbwid'], reverse=True)
									
		return None

class DocumentResource(Resource):
	
	CTS = fields.CharField(attribute='CTS')
	name = fields.CharField(attribute='name', null = True, blank = True)	
	name_eng = fields.CharField(attribute='name_eng', null = True, blank = True)
	lang = fields.CharField(attribute='lang', null = True, blank = True)
	author = fields.CharField(attribute='author', null = True, blank = True)
	sentences = fields.ListField(attribute='sentences', null = True, blank = True)
		
	class Meta:
		
		resource_name = 'document'
		object_class = DataObject
		authorization = ReadOnlyAuthorization()
	
	def detail_uri_kwargs(self, bundle_or_obj):
		
		kwargs = {}	
		if isinstance(bundle_or_obj, Bundle):
			kwargs['pk'] = bundle_or_obj.obj.id	
		else:
			kwargs['pk'] = bundle_or_obj.id		
		return kwargs
	
	#/api/word/?randomized=&format=json&lemma=κρατέω
	def get_object_list(self, request):
		
		gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)	
		attrlist = ['CTS', 'name', 'name_eng', 'lang', 'author']
		documents = []
		
		query_params = {}
		for obj in request.GET.keys():
			if obj in attrlist and request.GET.get(obj) is not None:
				query_params[obj] = request.GET.get(obj)
			elif obj.split('__')[0] in attrlist and request.GET.get(obj) is not None:
				query_params[obj] = request.GET.get(obj)
		
		# implement filtering
		if len(query_params) > 0:
			
			# generate query
			q = """START d=node(*) MATCH (d)-[:sentences]->(s) WHERE """
			
			# filter word on parameters
			for key in query_params:
				if len(key.split('__')) > 1:
					if key.split('__')[1] == 'contains':
						q = q + """HAS (d.""" +key.split('__')[0]+ """) AND d.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """.*' AND """
					elif key.split('__')[1] == 'startswith':
						q = q + """HAS (d.""" +key.split('__')[0]+ """) AND d.""" +key.split('__')[0]+ """=~'""" +query_params[key]+ """.*' AND """
					elif key.split('__')[1] == 'endswith':
						q = q + """HAS (d.""" +key.split('__')[0]+ """) AND d.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """' AND """
				else:
					q = q + """HAS (d.""" +key+ """) AND d.""" +key+ """='""" +query_params[key]+ """' AND """
			q = q[:len(q)-4]
			q = q + """RETURN DISTINCT d ORDER BY ID(d)"""
			
			table = gdb.query(q)
		
		# default querying	
		else:	
			table = gdb.query("""START d=node(*) MATCH (d)-[:sentences]->(s) WHERE HAS (s.CTS) RETURN DISTINCT d ORDER BY ID(d)""")
			
		# create the objects which was queried for and set all necessary attributes
		for t in table:
			document = t[0]		
			urlDoc = document['self'].split('/')		
				
			new_obj = DataObject(urlDoc[len(urlDoc)-1])
			new_obj.__dict__['_data'] = document['data']		
			new_obj.__dict__['_data']['id'] = urlDoc[len(urlDoc)-1]
			
			documentNode = gdb.nodes.get(document['self'])
			sentences = documentNode.relationships.outgoing(types=["sentences"])
			
			sentenceArray = []
			for s in range(0, len(sentences), 1):
				sent = sentences[s].end
				properties = {} #sent.properties #sent.properties['resource_uri']
				properties['resource_uri'] = API_PATH + 'sentence/' + str(sent.id) + '/'
				sentenceArray.append(properties)
				
			new_obj.__dict__['_data']['sentences'] = sentenceArray
			
			documents.append(new_obj)		
				
		return documents
	
	def obj_get_list(self, bundle, **kwargs):
		
		return self.get_object_list(bundle.request)
	
	def obj_get(self, bundle, **kwargs):
		
		gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)
		document = gdb.nodes.get(GRAPH_DATABASE_REST_URL + "node/" + kwargs['pk'] + '/')
		
		new_obj = DataObject(kwargs['pk'])
		new_obj.__dict__['_data'] = document.properties
		new_obj.__dict__['_data']['id'] = kwargs['pk']
		
		sentences = document.relationships.outgoing(types=["sentences"])
		sentenceArray = []
		for s in range(0, len(sentences), 1):
			sentence = sentences[s].end
			# this might seems a little hacky, but API resources are very decoupled,
			# which gives us great performance instead of creating relations amongst objects and referencing/dereferencing foreign keyed fields
			sentence.properties['resource_uri'] = API_PATH + 'sentence/' + str(sentence.id) + '/'
			sentenceArray.append(sentence.properties)
				
			new_obj.__dict__['_data']['sentences'] = sentenceArray

		return new_obj
 
   
"""
Visualization Resource.
"""
class VisualizationResource(Resource):
							
	class Meta:
		#queryset = Word.objects.all()
		resource_name = 'visualization'
		#always_return_data = True
		#excludes = ['require_order', 'require_all']
		authorization = ReadOnlyAuthorization()

	def prepend_urls(self, *args, **kwargs):	
		
		return [
			url(r"^(?P<resource_name>%s)/%s%s$" % (self._meta.resource_name, 'encountered', trailing_slash()), self.wrap_view('encountered'), name="api_%s" % 'encountered')
			]

	#/api/v1/visualization/encountered/?format=json&level=word&range=urn:cts:greekLit:tlg0003.tlg001.perseus-grc1:1.90.4:11-19&user=john
	def encountered(self, request, **kwargs):
		
		"""
		Start visualization...
		"""
		#fo = open("foo.txt", "wb")
		#millis = int(round(time.time() * 1000))
		#fo.write("%s start encountered method, get user: \n" % millis)
		
		gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)	
		submissions = gdb.query("""START n=node(*) MATCH (n)-[:submissions]->(s) WHERE HAS (n.username) AND n.username =  '""" + request.GET.get('user') + """' RETURN s""")	
		data = {}	
		
		if request.GET.get('level') == "word":
			
			seenDict = {}
			knownDict = {}
			data['words'] = []
		
			# calculate CTSs of the word range (later look them up within submissions of the user)
			wordRangeArray = []
			cts = request.GET.get('range')
			# get the stem
			endIndex = len(cts)-len(cts.split(':')[len(cts.split(':'))-1])
			rangeStem = cts[0:endIndex]		
			# get the numbers of the range and save the CTSs
			numbersArray = cts.split(':')[len(cts.split(':'))-1].split('-')
			for num in range(int(numbersArray[0]), int(numbersArray[1])+1):
				wordRangeArray.append(rangeStem + str(num))
			
			# get the file entry:
			filename = os.path.join(os.path.dirname(__file__), '../static/js/json/smyth.json')
			fileContent = {}
			with open(filename, 'r') as json_data:
				fileContent = json.load(json_data)
				json_data.close()
						
			for wordRef in wordRangeArray:
					
				w = gdb.query("""START n=node(*) MATCH (n) WHERE HAS (n.CTS) AND HAS (n.head) AND n.CTS = '""" +wordRef+ """' RETURN n""")
				
				seenDict[wordRef] = 0
				knownDict[wordRef] = False
				
				for sub in submissions.elements:	
				
					# get the morph info to the words via a file lookup of submission's smyth key, save params to test it on the encountered word of a submission
					params = {}
					grammarParams = fileContent[0][sub[0]['data']['smyth']]['query'].split('&')
					for pair in grammarParams:
						params[pair.split('=')[0]] = pair.split('=')[1]
														
					# get the encountered word's CTSs of this submission
					if wordRef in sub[0]['data']['encounteredWords']:			
												
						# if word learnt already known don't apply filter again
						if not knownDict[wordRef]:
							# loop over params to get morph known infos							
							badmatch = False
							
							for p in params.keys():
								try:
									w.elements[0][0]['data'][p]
									if params[p] != w.elements[0][0]['data'][p]:
										badmatch = True
								except KeyError as k:
									badmatch = True
									
							if not badmatch:
								knownDict[wordRef] = True				
										
						# if word in requested range and in encountered save times seen
						try:
							seenDict[wordRef]
							seenDict[wordRef] = seenDict[wordRef] + 1
						except KeyError as k:
							seenDict[wordRef] = 1
							
				# save data
				if seenDict[wordRef] > 0:
					data['words'].append({'value': w.elements[0][0]['data']['value'], 'timesSeen' : seenDict[wordRef], 'morphKnown': knownDict[wordRef], 'synKnown': False, 'vocKnown': True, 'CTS': w.elements[0][0]['data']['CTS']})
					#data['words'].append({'value': w.value, 'timesSeen' : seenDict[wordRef], 'morphKnown': knownDict[wordRef], 'synKnown': False, 'vocKnown': True, 'CTS': w.CTS})
				else:
					data['words'].append({'value': w.elements[0][0]['data']['value'], 'timesSeen' : seenDict[wordRef], 'morphKnown': knownDict[wordRef], 'synKnown': False, 'vocKnown': False, 'CTS': w.elements[0][0]['data']['CTS']})
					#data['words'].append({'value': w.value, 'timesSeen' : seenDict[wordRef], 'morphKnown': knownDict[wordRef], 'synKnown': False, 'vocKnown': False, 'CTS': w.CTS})
		
			return self.create_response(request, data)
		
		
		
		# if the viz of a document is requested calcualate the numbers on all submissions again and then the percentage of viz data
		elif request.GET.get('level') == "document":
			
			data['sentences'] = []

			# get the file entry:
			filename = os.path.join(os.path.dirname(__file__), '../static/js/json/smyth.json')
			fileContent = {}
			with open(filename, 'r') as json_data:
				fileContent = json.load(json_data)
				json_data.close()
				
			vocKnowledge = {}
			smythFlat = {}		
			# flatten the smyth and collect the vocab knowledge
			for sub in submissions.elements:			
				
				for word in sub[0]['data']['encounteredWords']:
					
					vocKnowledge[word] = True
					if sub[0]['data']['smyth'] not in smythFlat:
						# get the morph info via a file lookup of submission's smyth key, save params to test it on the words of the work
						params = {}
						grammarParams = fileContent[0][sub[0]['data']['smyth']]['query'].split('&')
						for pair in grammarParams:
							params[pair.split('=')[0]] = pair.split('=')[1]
						smythFlat[sub[0]['data']['smyth']] = params	
				
			# get the sentences of that document
			sentenceTable = gdb.query("""START n=node(*) MATCH (n)-[:sentences]->(s) WHERE HAS (s.CTS) AND n.CTS = '""" +request.GET.get('range')+ """' RETURN s""")
			#counter = 0
			for s in sentenceTable.elements:
				
				node = gdb.nodes.get(s[0]['self'])
				
				words = node.relationships.outgoing(types=["words"])
				all = {}	
				vocabKnown = {}
				morphKnown = {}
				syntaxKnown = {}
				
				for w in words:
				
					word = w.end
					all[word.properties['CTS']] = True
					morphKnown[word.properties['CTS']] = False
					vocabKnown[word.properties['CTS']] = False
					syntaxKnown[word.properties['CTS']] = False
					# scan the submission for vocab information
					for smyth in smythFlat:
							
						# was this word seen?
						if word.properties['CTS'] in vocKnowledge:	
							
							# if word morph already known don't apply filter again
							if not morphKnown[word.properties['CTS']]:
								# loop over params to get morph known infos
								badmatch = False
								for p in smythFlat[smyth].keys():
									try:
										word.properties[p]
										if params[p] != word.properties[p]:
											badmatch = True
									except KeyError as k:
										badmatch = True
								
								if not badmatch:
									morphKnown[word.properties['CTS']] = True # all params are fine				
							
							# know this vocab
							vocabKnown[word.properties['CTS']] = True
				
				# after reading words calcualte percentages of aspects for the sentence
				sentLeng = len(words)
				aspects = {'one': 0.00, 'two': 0.00, 'three': 0.00}
				for cts in all.keys():
					if vocabKnown[cts] and morphKnown[cts] and syntaxKnown[cts]:
						aspects['three'] = aspects['three'] +1
					elif vocabKnown[cts] and morphKnown[cts] or vocabKnown[cts] and syntaxKnown[cts] or morphKnown[cts] and syntaxKnown[cts]:
						aspects['two'] = aspects['two'] +1	
					elif vocabKnown[cts] or morphKnown[cts] or syntaxKnown[cts]:	
						aspects['one'] = aspects['one'] +1	
				
				# and save the infos to the json
				data['sentences'].append({'CTS': node.properties['CTS'], 'lenth': len(words), 'one': aspects['one']/len(words), 'two' : aspects['two']/len(words), 'three': aspects['three']/len(words)})
			
			return self.create_response(request, data)		
		
		return self.error_response(request, {'error': 'Level parameter required.'}, response_class=HttpBadRequest)
	
