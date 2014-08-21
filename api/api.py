from __future__ import unicode_literals
# coding: utf-8
from phaidra.settings import CTS_LANG
from phaidra.settings import GRAPH_DATABASE_REST_URL, API_PATH

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phaidra.settings")
from django.conf.urls import url
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout

from django.middleware.csrf import _get_new_csrf_key as get_new_csrf_key

from app.models import Textbook, Unit, Lesson, Slide, AppUser
from neo4jrestclient.client import GraphDatabase, Node, Relationship

from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.authentication import SessionAuthentication, BasicAuthentication, Authentication
from tastypie.authorization import Authorization, ReadOnlyAuthorization
from tastypie.utils import trailing_slash
from tastypie.http import HttpUnauthorized, HttpForbidden, HttpBadRequest
from tastypie.exceptions import NotFound, BadRequest, Unauthorized
from tastypie.resources import Resource, ModelResource
from tastypie.cache import SimpleCache
from tastypie.serializers import Serializer

from datetime import datetime

import dateutil.parser

import json
import operator
import time
import urlparse

class UserObjectsOnlyAuthorization(Authorization):
	
	def read_list(self, object_list, bundle):
		
		gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)	
		submissions = []
		table = gdb.query("""MATCH (u:`User`)-[:submits]->(s:`Submission`) WHERE HAS (u.username) AND u.username='""" + bundle.request.user.username + """' RETURN s""")		
			
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

class CreateUserResource(ModelResource):
	
	class Meta:
		queryset = AppUser.objects.all()
		resource_name = 'create_user'
		fields = ['username', 'first_name', 'last_name', 'last_login']
		allowed_methods = ['post']
		always_return_data = True
		authentication = Authentication()
		authorization = Authorization()
		
	def post_list(self, request, **kwargs):
		"""
		Make sure the user isn't already registered, create the user, return user object as JSON.
		"""
		self.method_check(request, allowed=['post'])		
		data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
			
		try:
			user = AppUser.objects.create_user(
				data.get("username"),
				data.get("email"),
				data.get("password")
			)
			user.save()
		except IntegrityError as e:
			return self.create_response(request, {
				'success': False,
				'error': e,
				'error_message': 'Username already in use.'
			})	
			
		body = json.loads(request.body) if type(request.body) is str else request.body
				
		return self.create_response(request, body)
		
						
class UserResource(ModelResource):
	class Meta:
		queryset = AppUser.objects.all()
		resource_name = 'user'
		fields = ['username', 'first_name', 'last_name', 'last_login']
		allowed_methods = ['get', 'post', 'patch']
		always_return_data = True
		authentication = SessionAuthentication()
		authorization = Authorization()

	def prepend_urls(self):
		params = (self._meta.resource_name, trailing_slash())
		return [
			url(r"^(?P<resource_name>%s)/login%s$" % params, self.wrap_view('login'), name="api_login"),
			url(r"^(?P<resource_name>%s)/logout%s$" % params, self.wrap_view('logout'), name="api_logout")
		]

	def login(self, request, **kwargs):
		"""
		Authenticate a user, create a CSRF token for them, and return the user object as JSON.
		"""
		self.method_check(request, allowed=['post'])
		
		data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))

		username = data.get('username', '')
		password = data.get('password', '')

		if username == '' or password == '':
			return self.create_response(request, {
				'success': False,
				'error_message': 'Missing username or password'
			})
		
		user = authenticate(username=username, password=password)
		
		if user:
			if user.is_active:
				login(request, user)
				response = self.create_response(request, {
					'success': True,
					'username': user.username
				})
				response.set_cookie("csrftoken", get_new_csrf_key())
				return response
			else:
				return self.create_response(request, {
					'success': False,
					'reason': 'disabled',
				}, HttpForbidden)
		else:
			return self.create_response(request, {
				'success': False,
				'error_message': 'Incorrect username or password'
			})
			
	def logout(self, request, **kwargs):
		""" 
		Attempt to log a user out, and return success status.		
		"""
		self.method_check(request, allowed=['get'])
		self.is_authenticated(request)
		if request.user and request.user.is_authenticated():
			logout(request)
			return self.create_response(request, { 'success': True })
		else:
			return self.create_response(request, { 'success': False, 'error_message': 'You are not authenticated, %s' % request.user.is_authenticated() })
	
	
	def patch_detail(self, request, **kwargs):
		""" 
		Check the user		
		"""
		self.method_check(request, allowed=['patch'])
		self.is_authenticated(request)
		if not request.user or not request.user.is_authenticated():
			return self.create_response(request, { 'success': False, 'error_message': 'You are not authenticated, %s' % request.user.is_authenticated() })
		else:	
		
			property_names = ['username', 'first_name', 'last_name', 'last_login', 'email', 'date_joined', 'lang', 'unit', 'lesson', 'progress']
			
			try:
				user = AppUser.objects.select_related(depth=1).get(id=kwargs["pk"])
			except ObjectDoesNotExist:
				raise Http404("Cannot find user.")
	
			body = json.loads(request.body) if type(request.body) is str else request.body
			data = body.copy()
	
			restricted_fields = ['is_staff', 'is_user', 'username', 'password']
	
			for field in body:
				if hasattr(user, field) and not field.startswith("_"):
					attr = getattr(user, field)
					value = data[field]
	
					# Do not alter relationship fields from this endpoint
					if not hasattr(attr, "_rel") and field not in restricted_fields:
						setattr(user, field, value)
					else:
						return self.create_response(request, {
							'success': False,
							'error_message': 'You are not authorized to update this field.'
						})
					continue
	
				# This field is not contained in our model, so discard it
				del data[field]
	
			if len(data) > 0:
				user.save()
	
			# Returns all field data of the related user as response data
			data = {}		
			for property_name in property_names: 		
				data[property_name] = getattr(user, property_name)
	
			return self.create_response(request, data)

"""
Simple object for creating the instances.
"""		
class DataObject(object):
	
    def __init__(self, id=None):
    	
    	self.__dict__['_data'] = {}
    	
    	if not hasattr(id, 'id') and id is not None:
    		
    		self.__dict__['_data']['id'] = id
       
    def __getattr__(self, name):
		if name.startswith('__'):
			raise AttributeError
		return self._data.get(name, None)

    def __setattr__(self, name, value):
        self.__dict__['_data'][name] = value

    def to_dict(self):
        return self._data
     

"""
Derives from Resource.
"""		
		
class SubmissionResource(Resource):
	
	response = fields.CharField(attribute='response', null = True, blank = True) 
	task = fields.CharField(attribute='task', null = True, blank = True)
	smyth = fields.CharField(attribute='smyth', null = True, blank = True)
	starttime = fields.DateField(attribute='starttime', null = True, blank = True)
	accuracy = fields.IntegerField(attribute='accuracy', null = True, blank = True)
	encounteredWords = fields.ListField(attribute='encounteredWords', null = True, blank = True)
	slideType = fields.CharField(attribute='slideType', null = True, blank = True)
	timestamp = fields.DateField(attribute='timestamp', null = True, blank = True)
	
	class Meta:
		object_class = DataObject
		resource_name = 'submission'
		allowed_methods = ['post', 'get', 'patch']
		authentication = SessionAuthentication() 
		authorization = UserObjectsOnlyAuthorization()	
		cache = SimpleCache(timeout=None)

	def detail_uri_kwargs(self, bundle_or_obj):
		
		kwargs = {}	
		if isinstance(bundle_or_obj, Bundle):
			kwargs['pk'] = bundle_or_obj.obj.id	
		else:
			kwargs['pk'] = bundle_or_obj.id		
		return kwargs

	# means csrftoken and sessionid  is required for reading, if resource on session auth?!
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
	
	# means csrftoken and sessionid  is required, if resource on session auth?!	
	def post_list(self, request, **kwargs):
		"""
		Create a new submission object, which relates to the slide it responds to and the user who submitted it.
		Return the submission object, complete with whether or not they got the answer correct.
		"""
		gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)
		
		self.method_check(request, allowed=['post'])
		self.is_authenticated(request)
		
		if not request.user or not request.user.is_authenticated():
			return self.create_response(request, { 'success': False, 'error_message': 'You are not authenticated, %s.' % request.user })

		data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))

		# check if thte authenticated and the data user has the same username
		#if request.user.username != data['user']:
			 #return self.create_response(request, { 'success': False, 'error_message': 'Authenticated and submitting user is not identical, authenticated: %s , submitting: %s' % (request.user, data['user'])})

		# get the user via neo look-up or create a newone
		if request.user.username is not None:
			userTable = gdb.query("""MATCH (u:`User`)-[:submits]->(s:`Submission`) WHERE HAS (u.username) AND u.username='""" + request.user.username + """' RETURN u""")
		
			if len(userTable) > 0:	
				userurl = userTable[0][0]['self']
				userNode = gdb.nodes.get(userurl)			
			
			else:
				userNode = gdb.nodes.create(username=request.user.username)
				userNode.labels.add("User")
			
			
			subms = gdb.nodes.create(
				response = data.get("response"),
				task = data.get("task"), 
				smyth = data.get("smyth"),	# string
				starttime = data.get("starttime"),	 # catch this so that it doesn't lead to submission problems
				accuracy = data.get("accuracy"),
				encounteredWords = data.get("encounteredWords"), # array
				slideType = data.get("slideType"),
				timestamp = data.get("timestamp") 
			)
			
			subms.labels.add("Submission")
			
			if subms is None :
				# in case an error wasn't already raised 			
				raise ValidationError('Submission node could not be created.')
		
			# Form the connections from the new Submission node to the existing slide and user nodes
			userNode.submits(subms)
	
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
		object_class = DataObject	
		resource_name = 'lemma'		
		authorization = ReadOnlyAuthorization()
		cache = SimpleCache(timeout=None)
	
	def detail_uri_kwargs(self, bundle_or_obj):
		
		kwargs = {}
		if isinstance(bundle_or_obj, Bundle):
			kwargs['pk'] = bundle_or_obj.obj.id			
		else:
			kwargs['pk'] = bundle_or_obj.id			
		return kwargs
	
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
			q = """MATCH (l:`Lemma`)-[:values]->(w:`Word`) WHERE """
			
			# filter word on parameters
			for key in query_params:
				if len(key.split('__')) > 1:
					if key.split('__')[1] == 'contains':
						q = q + """HAS (l.""" +key.split('__')[0]+ """) AND l.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """.*' AND """
					elif key.split('__')[1] == 'startswith':
						q = q + """HAS (l.""" +key.split('__')[0]+ """) AND l.""" +key.split('__')[0]+ """=~'""" +query_params[key]+ """.*' AND """
					elif key.split('__')[1] == 'endswith':
						q = q + """HAS (l.""" +key.split('__')[0]+ """) AND l.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """' AND """
					elif key.split('__')[1] == 'isnot':
						q = q + """HAS (l.""" +key.split('__')[0]+ """) AND l.""" +key.split('__')[0]+ """<>'""" +query_params[key]+ """' AND """
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
			table = gdb.query("""MATCH (l:`Lemma`)-[:values]->(w:`Word`) WHERE HAS (l.CITE) RETURN DISTINCT l ORDER BY ID(l)""")
			
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
	
	CTS = fields.CharField(attribute='CTS', null = True, blank = True)
	value = fields.CharField(attribute='value', null = True, blank = True)
	form = fields.CharField(attribute='form', null = True, blank = True)
	lemma = fields.CharField(attribute='lemma', null = True, blank = True)
	ref = fields.CharField(attribute='ref', null = True, blank = True)
	lang = fields.CharField(attribute='lang', null = True, blank = True)
	
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
		object_class = DataObject
		resource_name = 'word'
		authorization = ReadOnlyAuthorization()
		cache = SimpleCache(timeout=None)
	
	def prepend_urls(self, *args, **kwargs):	
		
		return [
			url(r"^(?P<resource_name>%s)/%s%s$" % (self._meta.resource_name, 'smyth', trailing_slash()), self.wrap_view('smyth'), name="api_%s" % 'smyth')
			]
	
	"""
	returns a list of words to a given smyth key. Doesn't work via objects. Returns a json object returninig a list of words.
	"""
	def smyth(self, request, **kwargs):
		gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)
		data = {}
		data['words'] = []
		query_params = {}
		
		# this might tricky, because no error response creatable of unsuccessful
		if request.GET.get('smyth'):
			
			# get the file entry:
			filename = os.path.join(os.path.dirname(__file__), '../static/js/json/smyth.json')
			fileContent = {}
			with open(filename, 'r') as json_data:
				fileContent = json.load(json_data)
				json_data.close()
				
			try:
				grammarParams = fileContent[0][request.GET.get('smyth')]['query'].split('&')		
				for pair in grammarParams:
					query_params[pair.split('=')[0]] = pair.split('=')[1]
			except KeyError as k:	
				return self.error_response(request, {'error': 'Smyth key does not exist.'}, response_class=HttpBadRequest)
			
			# generate query
			q = """MATCH (s:`Sentence`)-[:words]->(w:`Word`) WHERE """
			
			# filter word on parameters
			for key in query_params:
				if len(key.split('__')) > 1:
					if key.split('__')[1] == 'contains':
						q = q + """HAS (w.""" +key.split('__')[0]+ """) AND w.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """.*' AND """
					elif key.split('__')[1] == 'startswith':
						q = q + """HAS (w.""" +key.split('__')[0]+ """) AND w.""" +key.split('__')[0]+ """=~'""" +query_params[key]+ """.*' AND """
					elif key.split('__')[1] == 'endswith':
						q = q + """HAS (w.""" +key.split('__')[0]+ """) AND w.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """' AND """
					elif key.split('__')[1] == 'isnot':
						q = q + """HAS (w.""" +key.split('__')[0]+ """) AND w.""" +key.split('__')[0]+ """<>'""" +query_params[key]+ """' AND """
				else:
					q = q + """HAS (w.""" +key+ """) AND w.""" +key+ """='""" +query_params[key]+ """' AND """
			q = q[:len(q)-4]
			q = q + """RETURN w, s ORDER BY ID(w)"""
			
			table = gdb.query(q)
				
			# create the objects which was queried for and set all necessary attributes
			for t in table:
				word = t[0]
				sentence = t[1]		
				url = word['self'].split('/')
				urlSent = sentence['self'].split('/')		
				
				tmp = {}
				for key in word['data']:
					tmp[key] = word['data'][key]	
				tmp['resource_uri'] = API_PATH + 'word/' + url[len(url)-1]
				tmp['sentence_resource_uri'] = API_PATH + 'sentence/' + urlSent[len(urlSent)-1] +'/'
				data['words'].append(tmp)
			
			return self.create_response(request, data)
		
		else:
			return self.error_response(request, {'error': 'Smyth key missed.'}, response_class=HttpBadRequest)
	
	def detail_uri_kwargs(self, bundle_or_obj):
		
		kwargs = {}		
		if isinstance(bundle_or_obj, Bundle):
			kwargs['pk'] = bundle_or_obj.obj.id
		else:
			kwargs['pk'] = bundle_or_obj.id
		return kwargs
	
	def get_object_list(self, request):
		
		gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)
		attrlist = ['lang','CTS', 'length', 'case', 'dialect', 'head', 'form', 'posClass', 'cid', 'gender', 'tbwid', 'pos', 'value', 'degree', 'number','lemma', 'relation', 'isIndecl', 'ref', 'posAdd', 'mood', 'tense', 'voice', 'person']
		words = []
		query_params = {}
		
		if request.GET.get('smyth'):
			
			# get the file entry:
			filename = os.path.join(os.path.dirname(__file__), '../static/js/json/smyth.json')
			fileContent = {}
			with open(filename, 'r') as json_data:
				fileContent = json.load(json_data)
				json_data.close()
				
			try:
				grammarParams = fileContent[0][request.GET.get('smyth')]['query'].split('&')		
				for pair in grammarParams:
					query_params[pair.split('=')[0]] = pair.split('=')[1]
			except KeyError as k:	
				return words				
		
		# query by ordinary filters		
		for obj in request.GET.keys():
			if obj in attrlist and request.GET.get(obj) is not None:
				query_params[obj] = request.GET.get(obj)
			elif obj.split('__')[0] in attrlist and request.GET.get(obj) is not None:
				query_params[obj] = request.GET.get(obj)
		
		# implement filtering
		if len(query_params) > 0:
			
			# generate query
			q = """MATCH (s:`Sentence`)-[:words]->(w:`Word`) WHERE """
			
			# filter word on parameters
			for key in query_params:
				if key in ['tbwid', 'head', 'length', 'cid']:
					q = q + """HAS (w.""" +key+ """) AND w.""" +key+ """=""" +query_params[key]+ """ AND """
				else:				
					if len(key.split('__')) > 1:
						if key.split('__')[1] == 'contains':
							q = q + """HAS (w.""" +key.split('__')[0]+ """) AND w.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """.*' AND """
						elif key.split('__')[1] == 'startswith':
							q = q + """HAS (w.""" +key.split('__')[0]+ """) AND w.""" +key.split('__')[0]+ """=~'""" +query_params[key]+ """.*' AND """
						elif key.split('__')[1] == 'endswith':
							q = q + """HAS (w.""" +key.split('__')[0]+ """) AND w.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """' AND """
						elif key.split('__')[1] == 'isnot':
							q = q + """HAS (w.""" +key.split('__')[0]+ """) AND w.""" +key.split('__')[0]+ """<>'""" +query_params[key]+ """' AND """
					else:
						q = q + """HAS (w.""" +key+ """) AND w.""" +key+ """='""" +query_params[key]+ """' AND """
			q = q[:len(q)-4]
			q = q + """RETURN w, s ORDER BY ID(w)"""
			
			table = gdb.query(q)
			
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
						
				words.append(new_obj)
				
			return words	
		
		# default querying on big dataset
		else:	

			documentTable = gdb.query("""MATCH (n:`Document`) RETURN n ORDER BY ID(n)""")	
			
			for d in documentTable:
				document = d[0]
				wordTable = gdb.query("""MATCH (d:`Document`)-[:sentences]->(s:`Sentence`)-[:words]->(w:`Word`) WHERE d.CTS = '""" + document['data']['CTS'] + """' RETURN w,s ORDER BY ID(w)""")
							
				# get sent id
				for w in wordTable:
					word = w[0]
					sentence = w[1]
					url = word['self'].split('/')
					urlSent = sentence['self'].split('/')	
						
					new_obj = DataObject(url[len(url)-1])
					new_obj.__dict__['_data'] = word['data']
									
					new_obj.__dict__['_data']['id'] = url[len(url)-1]
					new_obj.__dict__['_data']['sentence_resource_uri'] = API_PATH + 'sentence/' + urlSent[len(urlSent)-1] +'/'
									
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
			
		translations = gdb.query("""MATCH (d:`Word`)-[:translation]->(w:`Word`) WHERE d.CTS='""" +word.properties['CTS']+ """' RETURN DISTINCT w ORDER BY ID(w)""")
		translationArray = []
		for t in translations:
			trans = t[0]
			url = trans['self'].split('/')
			trans['data']['resource_uri'] = API_PATH + 'word/' + url[len(url)-1] + '/'
			translationArray.append(trans['data'])
				
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
		object_class = DataObject
		resource_name = 'sentence'	
		authorization = ReadOnlyAuthorization()	
		cache = SimpleCache(timeout=None)
	
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
			q = """MATCH (d:`Document`)-[:sentences]->(s:`Sentence`) WHERE """
			
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
			table = gdb.query("""MATCH (d:`Document`)-[:sentences]->(s:`Sentence`) WHERE HAS (s.CTS) RETURN s, d ORDER BY ID(s)""")
			
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
		
		# get a dictionary of related translation of this sentence # ordering here is a problem child
		relatedSentences = gdb.query("""MATCH (s:`Sentence`)-[:words]->(w:`Word`)-[:translation]->(t:`Word`)<-[:words]-(s1:`Sentence`) WHERE HAS (s.CTS) AND s.CTS='"""+ sentence.properties['CTS'] + """' RETURN DISTINCT s1 ORDER BY ID(s1)""")

		
		new_obj.__dict__['_data']['translations']={}
		for rs in relatedSentences:
			sent = rs[0]
			url = sent['self'].split('/')
			for lang in CTS_LANG:
				if sent['data']['CTS'].find(lang) != -1:
					new_obj.__dict__['_data']['translations'][lang] = API_PATH + 'sentence/' + url[len(url)-1] +'/'		
		
		# get the words	and related information	
		words = gdb.query("""MATCH (d:`Sentence`)-[:words]->(w:`Word`) WHERE d.CTS='""" +sentence.properties['CTS']+ """' RETURN DISTINCT w ORDER BY ID(w)""")
		wordArray = []
		for w in words:
			word = w[0]
			url = word['self'].split('/')
			word['data']['resource_uri'] = API_PATH + 'word/' + url[len(url)-1] + '/'
			wordNode = gdb.nodes.get(GRAPH_DATABASE_REST_URL + "node/" + url[len(url)-1] + '/')
			
			# get the lemma	
			lemmaRels = wordNode.relationships.incoming(types=["values"])
			if len(lemmaRels) > 0:
				word['data']['lemma_resource_uri'] = API_PATH + 'lemma/' + str(lemmaRels[0].start.id) + '/'
			
			# get the full translation # forse API into full representation if cache is enabled
			#if bundle.request.GET.get('full'):			
			translations = gdb.query("""MATCH (d:`Word`)-[:translation]->(w:`Word`) WHERE d.CTS='""" +wordNode.properties['CTS']+ """' RETURN DISTINCT w ORDER BY ID(w)""")
			translationArray = []
			for t in translations:
				trans = t[0]
				transurl = trans['self'].split('/')
				trans['data']['resource_uri'] = API_PATH + 'word/' + transurl[len(transurl)-1] + '/'
				translationArray.append(trans['data'])
			word['data']['translations'] = translationArray
				
			wordArray.append(word['data'])
			
		# if short=True return only words of the short sentence
		if bundle.request.GET.get('short'):
			wordArray = self.shorten(wordArray, query_params)
			if wordArray is None:
				#return None
				raise BadRequest("Sentence doesn't hit your query.")
		
		
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
			if w['head'] != 0:
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
								#aim_words.append(w.value) # Is are checked later
					
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
					
				# refinement of u coords # i want u if i is not empty
				for id in u:
					for id2 in i:
						w = nodes[id2].value
						if w['head'] == id:
							aim_words.append(w)
					if len(i) > 0:
						w2 = nodes[id].value
						aim_words.append(w2)
						  
							
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
								return sorted(aim_words, key=lambda x: x['tbwid'])	
						
						return None		
					else:		
						# set and order words
						return sorted(aim_words, key=lambda x: x['tbwid'])				
					
					# set and order words
					return sorted(aim_words, key=lambda x: x['tbwid'])
									
		return None

class DocumentResource(Resource):
	
	CTS = fields.CharField(attribute='CTS')
	lang = fields.CharField(attribute='lang', null = True, blank = True)	
	sentences = fields.ListField(attribute='sentences', null = True, blank = True)
	name = fields.CharField(attribute='name', null = True, blank = True)
	author = fields.CharField(attribute='author', null = True, blank = True)
	translations = fields.DictField(attribute='translations', null = True, blank = True)
	
	class Meta:
		object_class = DataObject
		resource_name = 'document'	
		authorization = ReadOnlyAuthorization()
		cache = SimpleCache(timeout=None)
	
	def detail_uri_kwargs(self, bundle_or_obj):
		
		kwargs = {}	
		if isinstance(bundle_or_obj, Bundle):
			kwargs['pk'] = bundle_or_obj.obj.id	
		else:
			kwargs['pk'] = bundle_or_obj.id		
		return kwargs
	
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
			q = """MATCH (d:`Document`)-[:sentences]->(s:`Sentence`) WHERE """
			
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
			table = gdb.query("""MATCH (d:`Document`) RETURN DISTINCT d ORDER BY ID(d)""")
			
		# create the objects which was queried for and set all necessary attributes
		for t in table:
			document = t[0]		
			urlDoc = document['self'].split('/')		
				
			new_obj = DataObject(urlDoc[len(urlDoc)-1])
			new_obj.__dict__['_data'] = document['data']		
			new_obj.__dict__['_data']['id'] = urlDoc[len(urlDoc)-1]
			
			#documentNode = gdb.nodes.get(document['self'])
			#sentences = documentNode.relationships.outgoing(types=["sentences"])
	
			sentences = gdb.query("""MATCH (d:`Document`)-[:sentences]->(s:`Sentence`) WHERE d.CTS='""" +document['data']['CTS']+ """' RETURN DISTINCT s ORDER BY ID(s)""")
			sentenceArray = []
			for s in sentences:
				
				sent = s[0]
				url = sent['self'].split('/')
				# this might seems a little hacky, but API resources are very decoupled,
				# which gives us great performance instead of creating relations amongst objects and referencing/dereferencing foreign keyed fields
				sent['data'] = {}
				sent['data']['resource_uri'] = API_PATH + 'sentence/' + url[len(url)-1] + '/'
				sentenceArray.append(sent['data'])
				
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
		
		sentences = gdb.query("""MATCH (d:`Document`)-[:sentences]->(s:`Sentence`) WHERE d.CTS='""" +document.properties['CTS']+ """' RETURN DISTINCT s ORDER BY ID(s)""")
		sentenceArray = []
		for s in sentences:
			sent = s[0]
			url = sent['self'].split('/')
			# this might seems a little hacky, but API resources are very decoupled,
			# which gives us great performance instead of creating relations amongst objects and referencing/dereferencing foreign keyed fields
			sent['data']['resource_uri'] = API_PATH + 'sentence/' + url[len(url)-1] + '/'
			sentenceArray.append(sent['data'])
				
			new_obj.__dict__['_data']['sentences'] = sentenceArray
			
		
		# get a dictionary of related translations of this document
		relatedDocuments = gdb.query("""MATCH (d:`Document`)-[:sentences]->(s:`Sentence`)-[:words]->(w:`Word`)-[:translation]->(t:`Word`)<-[:words]-(s1:`Sentence`)<-[:sentences]-(d1:`Document`) WHERE HAS (d.CTS) AND d.CTS='"""+ document.properties['CTS'] +"""' RETURN DISTINCT d1 ORDER BY ID(d1)""")
		
		new_obj.__dict__['_data']['translations']={}
		for rd in relatedDocuments:
			doc = rd[0]
			url = doc['self'].split('/')
			if doc['data']['lang'] in CTS_LANG:
				new_obj.__dict__['_data']['translations'][doc['data']['lang']] = doc['data']
				new_obj.__dict__['_data']['translations'][doc['data']['lang']]['resource_uri']= API_PATH + 'document/' + url[len(url)-1] +'/'


		return new_obj
 
   
"""
Visualization Resource.
"""
class VisualizationResource(Resource):
							
	class Meta:
		#queryset = Word.objects.all()
		resource_name = 'visualization'
		authorization = ReadOnlyAuthorization()

	def prepend_urls(self, *args, **kwargs):	
		
		return [
			url(r"^(?P<resource_name>%s)/%s%s$" % (self._meta.resource_name, 'encountered', trailing_slash()), self.wrap_view('encountered'), name="api_%s" % 'encountered'),
			url(r"^(?P<resource_name>%s)/%s%s$" % (self._meta.resource_name, 'statistics', trailing_slash()), self.wrap_view('statistics'), name="api_%s" % 'statistics'),
			url(r"^(?P<resource_name>%s)/%s%s$" % (self._meta.resource_name, 'least_accurate', trailing_slash()), self.wrap_view('least_accurate'), name="api_%s" % 'least_accurate'),
			url(r"^(?P<resource_name>%s)/%s%s$" % (self._meta.resource_name, 'least_recently', trailing_slash()), self.wrap_view('least_recently'), name="api_%s" % 'least_recently')
			]
		
	"""
	prepare knowledge map
	"""
	def calculateKnowledgeMap(self, user):
		
		gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)	
		submissions = gdb.query("""MATCH (n:`User`)-[:submits]->(s:`Submission`) WHERE HAS (n.username) AND n.username =  '""" + user + """' RETURN s""")	
		
		# get the file entry:
		filename = os.path.join(os.path.dirname(__file__), '../static/js/json/smyth.json')
		fileContent = {}
		with open(filename, 'r') as json_data:
			fileContent = json.load(json_data)
			json_data.close()			
						
		vocab = {}
		smyth = {}		
		lemmas = {}
		lemmaFreq = 0
		# flatten the smyth and collect the vocab knowledge
		for sub in submissions.elements:			
			
			try: 	
				for word in sub[0]['data']['encounteredWords']:
						
					try:
						vocab[word] = vocab[word]+1
					except KeyError as k:
						vocab[word] = 1
						# if vocab appears first time, get the lemmas frequency (two vocs can have same lemma, so save lemma as key)
						try:
							lemma = gdb.query("""MATCH (l:`Lemma`)-[:values]->(n:`Word`) WHERE n.CTS = '""" + word + """' RETURN l.value, l.frequency""")
							if lemma.elements[0][0] is not None and lemma.elements[0][0] != "":
								lemmas[lemma.elements[0][0]] = lemma.elements[0][1]
						# in case of weird submission test data for encounteredWords
						except IndexError as i:
							continue
					if sub[0]['data']['smyth'] not in smyth:
						# get the morph info via a file lookup of submission's smyth key, save params to test it on the words of the work
						params = {}
						try:
							grammarParams = fileContent[0][sub[0]['data']['smyth']]['query'].split('&')
							for pair in grammarParams:
								params[pair.split('=')[0]] = pair.split('=')[1]
							smyth[sub[0]['data']['smyth']] = params
						except KeyError as k:
							continue
			except KeyError as k:
				continue
		
		# get the lemma/vocab overall count
		for freq in lemmas:
			lemmaFreq = lemmaFreq + int(lemmas[freq])

		return [vocab, smyth, lemmaFreq]
	
	
	def check_fuzzy_filters(self, filter, request_attribute, word_attribute ):
		
		if filter == 'contains':
			if request_attribute not in word_attribute:
				return True
		elif filter == 'startswith':	
			if not word_attribute.startswith(request_attribute):
				return True
		elif filter == 'endswith':
			if not word_attribute.endswith(request_attribute):
				return True
		elif filter == 'isnot':	
			if word_attribute == request_attribute:
				return True
			
		return False


	"""
	returns visualization data on word-rage-, book- and work-level.
	"""
	def encountered(self, request, **kwargs):
		
		data = {}
		gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)
		#fo = open("foo.txt", "wb")
		#millis = int(round(time.time() * 1000))
		#fo.write("%s start encountered method, get user: \n" % millis)	
		
		# /api/v1/visualization/encountered/?format=json&level=word&range=urn:cts:greekLit:tlg0003.tlg001.perseus-grc1:1.90.4:11-19&user=john
		if request.GET.get('level') == "word":
			
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
			####### make a error code wront range format here
			for num in range(int(numbersArray[0]), int(numbersArray[1])+1):
				wordRangeArray.append(rangeStem + str(num))
			
			# preprocess knowledge of a user
			callFunction = self.calculateKnowledgeMap(request.GET.get('user'))
			vocKnowledge = callFunction[0]
			smythFlat = callFunction[1]
								
			for wordRef in wordRangeArray:
					
				w = gdb.query("""MATCH (n:`Word`) WHERE HAS (n.CTS) AND HAS (n.head) AND n.CTS = '""" +wordRef+ """' RETURN n""")
				
				knownDict[wordRef] = False
				
				#for sub in submissions.elements:
				for smyth in smythFlat:		
					# was the word even known?
					if wordRef in vocKnowledge:			
			
						# loop over params to get morph known infos							
						badmatch = False			
						for p in smythFlat[smyth].keys():
							try:
								w.elements[0][0]['data'][p]
								if smythFlat[smyth][p] != w.elements[0][0]['data'][p]:
									badmatch = True
									break
							# check for fuzzy filtering attributes
							except KeyError as k:
								if len(p.split('__')) > 1:
									try:
										badmatch = self.check_fuzzy_filters(p.split('__')[1], smythFlat[smyth][p], w.elements[0][0]['data'][p.split('__')[0]])
									except KeyError as k:
										badmatch = True
										break																	
								else:
									badmatch = True
									break
									
						if not badmatch:
							knownDict[wordRef] = True												
							
				# save data
				try:
					data['words'].append({'value': w.elements[0][0]['data']['value'], 'timesSeen' : vocKnowledge[wordRef], 'morphKnown': knownDict[wordRef], 'synKnown': False, 'vocKnown': True, 'CTS': w.elements[0][0]['data']['CTS']})
				except KeyError as e:
					##### here might goes the sentence end error code
					data['words'].append({'value': w.elements[0][0]['data']['value'], 'timesSeen' : 0, 'morphKnown': knownDict[wordRef], 'synKnown': False, 'vocKnown': False, 'CTS': w.elements[0][0]['data']['CTS']})
					
			return self.create_response(request, data)
		
		
		# if the viz of a book is requested calcualate the numbers on all submissions and then the percentage of viz data
		# /api/v1/visualization/encountered/?format=json&level=book&range=urn:cts:greekLit:tlg0003.tlg001.perseus-grc1:1&user=john
		elif request.GET.get('level') == "book":
			
			knownDict = {}
			data['words'] = []
							
			# preprocess knowledge of a user
			callFunction = self.calculateKnowledgeMap(request.GET.get('user'))
			vocKnowledge = callFunction[0]
			smythFlat = callFunction[1]
								
			# get the sentences of that document
			sentenceTable = gdb.query("""MATCH (n:`Document`)-[:sentences]->(s:`Sentence`) WHERE HAS (s.CTS) AND n.CTS = '""" +request.GET.get('range')+ """' RETURN s ORDER BY ID(s)""")
			
			for s in sentenceTable.elements:
				
				node = gdb.nodes.get(s[0]['self'])			
				#words = node.relationships.outgoing(types=["words"])
				
				words = gdb.query("""MATCH (s:`Sentence`)-[:words]->(w:`Word`) WHERE s.CTS = '""" +node.properties['CTS']+ """' RETURN w ORDER BY ID(w)""")
				
				for w in words:
					word = w[0]
					#word = gdb.nodes.get(w[0]['self'])	
					knownDict[word['data']['CTS']] = False
				
					for smyth in smythFlat:		
						
						# scan the submission for vocab information
						if word['data']['CTS'] in vocKnowledge:			
			
							# loop over params to get morph known infos
							# extract this maybe (hand over smyth, its value and word)							
							badmatch = False			
							for p in smythFlat[smyth].keys():
								try:
									word['data'][p]
									if smythFlat[smyth][p] != word['data'][p]:
										badmatch = True
										break
								# check for fuzzy filtering attributes
								except KeyError as k:
									if len(p.split('__')) > 1:
										try:
											badmatch = self.check_fuzzy_filters(p.split('__')[1], smythFlat[smyth][p], word['data'][p.split('__')[0]])
										except KeyError as k:
											badmatch = True
											break																					
									else:
										badmatch = True
										break
									
							if not badmatch:
								knownDict[word['data']['CTS']] = True												
							
					# save data
					try:
						data['words'].append({'value': word['data']['value'], 'timesSeen' : vocKnowledge[word['data']['CTS']], 'morphKnown': knownDict[word['data']['CTS']], 'synKnown': False, 'vocKnown': True, 'CTS': word['data']['CTS']})
					except KeyError as e:
						data['words'].append({'value': word['data']['value'], 'timesSeen' : 0, 'morphKnown': knownDict[word['data']['CTS']], 'synKnown': False, 'vocKnown': False, 'CTS': word['data']['CTS']})
						
			return self.create_response(request, data)
			
		
		# if the viz of a document is requested calcualate the numbers on all submissions and then the percentage of viz data
		# /api/v1/visualization/encountered/?format=json&level=document&range=urn:cts:greekLit:tlg0003.tlg001.perseus-grc1:1&user=john
		elif request.GET.get('level') == "document":
			
			data['sentences'] = []
				
			# preprocess knowledge of a user
			callFunction = self.calculateKnowledgeMap(request.GET.get('user'))
			vocKnowledge = callFunction[0]
			smythFlat = callFunction[1]
				
			# get the sentences of that document
			sentenceTable = gdb.query("""MATCH (n:`Document`)-[:sentences]->(s:`Sentence`) WHERE HAS (s.CTS) AND n.CTS = '""" +request.GET.get('range')+ """' RETURN s ORDER BY ID(s)""")
			
			for s in sentenceTable.elements:
				
				node = gdb.nodes.get(s[0]['self'])			
				words = node.relationships.outgoing(types=["words"])
				
				# helper arrays also for statistics, contain the cts as a key and a boolean as an entry
				all = {}	
				vocabKnown = {}
				morphKnown = {}
				syntaxKnown = {}
				
				for w in words:
				
					word = w.end
					all[word.properties['CTS']] = True
					vocabKnown[word.properties['CTS']] = False
					morphKnown[word.properties['CTS']] = False
					syntaxKnown[word.properties['CTS']] = False
					# scan the submission for vocab information
					for smyth in smythFlat:
						# was this word seen?
						if word.properties['CTS'] in vocKnowledge:	
							
							# if word morph already known don't apply filter again
							if morphKnown[word.properties['CTS']]:
								# loop over params to get morph known infos
								badmatch = False
								for p in smythFlat[smyth].keys():
									try:
										word.properties[p]
										if smythFlat[smyth][p] != word.properties[p]:
											badmatch = True
											break
									# check for fuzzy filtering attributes
									except KeyError as k:
										if len(p.split('__')) > 1:
											try:
												badmatch = self.check_fuzzy_filters(p.split('__')[1], smythFlat[smyth][p], word.properties[p.split('__')[0]])
											except KeyError as k:
												badmatch = True
												break																					
										else:
											badmatch = True
											break
								
								if not badmatch:
									morphKnown[word.properties['CTS']] = True # all params are fine											
							
							# know this vocab
							vocabKnown[word.properties['CTS']] = True
				
				# after reading words calcualte percentages of aspects for the sentence
				sentLeng = len(words)
				aspects = {'one': 0.0, 'two': 0.0, 'three': 0.0}
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
	
	
	"""
	Returns overall statistically learned information for displaying in the panels
	"""
	def statistics(self, request, **kwargs):
		
		data = {}
		gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)
		
		# preprocess knowledge of a user
		callFunction = self.calculateKnowledgeMap(request.GET.get('user'))
		vocKnowledge = callFunction[0]
		smythFlat = callFunction[1]
		lemmaFreqs = callFunction[2]
			
		# get the sentences of that document
		sentenceTable = gdb.query("""MATCH (n:`Document`)-[:sentences]->(s:`Sentence`) WHERE HAS (s.CTS) AND n.CTS = '""" +request.GET.get('range')+ """' RETURN s""")
		
		# helper arrays also for statistics, contain the cts as a key and a boolean as an entry
		all = {}	
		vocabKnown = {}
		morphKnown = {}
		syntaxKnown = {}
		wordCount = 0
		for s in sentenceTable.elements:
			
			node = gdb.nodes.get(s[0]['self'])			
			words = node.relationships.outgoing(types=["words"])
				
			for w in words:
			
				word = w.end
				all[word.properties['CTS']] = True
				# compare all smyth keys the user knows to the actual word's morphology
				for smyth in smythFlat:
					# if word morph already known (earlier smyth hit), don't apply filter again
					try:
						morphKnown[word.properties['CTS']]
					except KeyError as k:
						# loop over params to get morph known infos
						badmatch = False
						for p in smythFlat[smyth].keys():
							try:
								word.properties[p]
								if smythFlat[smyth][p] != word.properties[p]:
									badmatch = True
									break
							# check for fuzzy filtering attributes
							except KeyError as k:
								if len(p.split('__')) > 1:
									try:
										badmatch = self.check_fuzzy_filters(p.split('__')[1], smythFlat[smyth][p], word.properties[p.split('__')[0]])
									except KeyError as k:
										badmatch = True
										break																					
								else:
									badmatch = True
									break
						
						if not badmatch:
							morphKnown[word.properties['CTS']] = True # all params are fine											

			# after reading words update overall no
			wordCount = wordCount + len(words)
		
		# after reading everything return the statistics
		data['statistics'] = {'all': wordCount, 'vocab': float(lemmaFreqs)/float(len(all)), 'morphology': float(len(morphKnown))/float(len(all)), 'syntax': float(len(syntaxKnown))/float(len(all))}
	
		return self.create_response(request, data)
	
	
	"""
	Returns some figures for grammar and title the user has struggled with
	"""
	def least_accurate(self, request, **kwargs):
		
		data = {}
		data['accuracy_ranking'] = []
		gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)
		
		accuracy = {}
		title = {}
		query = {}

		# get the file smyth entry:
		filename = os.path.join(os.path.dirname(__file__), '../static/js/json/smyth.json')
		fileContent = {}
		with open(filename, 'r') as json_data:
			fileContent = json.load(json_data)
			json_data.close()			

		for entry in fileContent[0].keys():
			query[entry] = fileContent[0][entry]['query']
			title[entry] = fileContent[0][entry]['title']

		# process accuracy of grammar of submissions of a user
		gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)	
		submissions = gdb.query("""MATCH (n:`User`)-[:submits]->(s:`Submission`) WHERE HAS (n.username) AND n.username =  '""" + request.GET.get('user') + """' RETURN s""")			
									
		# get the accuray per smyth key
		for sub in submissions.elements:
			if sub[0]['data']['accuracy'] < 50:								
				try:
					accuracy[sub[0]['data']['smyth']].append(sub[0]['data']['accuracy'])  
				except KeyError as k:
					accuracy[sub[0]['data']['smyth']] = []
					accuracy[sub[0]['data']['smyth']].append(sub[0]['data']['accuracy'])
		
		# calculate the averages and sort by it
		average = {}
		for smyth in accuracy.keys():
			average[smyth] = 0.0
			for value in accuracy[smyth]:
				average[smyth] = average[smyth] + value
			average[smyth] = average[smyth]/len(accuracy[smyth]) 
		
		sorted_dict = sorted(average.iteritems(), key=operator.itemgetter(1))
		#sorted_reverse = sorted.reverse()
				
		for entry in sorted_dict:
			data['accuracy_ranking'].append({'smyth': entry[0], 'average': average[entry[0]], 'title': title[entry[0]], 'query': query[entry[0]]})
	
		#return the json
		return self.create_response(request, data)
	
	
	"""
	Returns some figures for grammar and title the user has struggled with
	"""
	def least_recently(self, request, **kwargs):
		
		data = {}
		data['time_ranking'] = []
		gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)
		
		time = {}
		title = {}
		query = {}

		# get the file smyth entry:
		filename = os.path.join(os.path.dirname(__file__), '../static/js/json/smyth.json')
		fileContent = {}
		with open(filename, 'r') as json_data:
			fileContent = json.load(json_data)
			json_data.close()			

		for entry in fileContent[0].keys():
			query[entry] = fileContent[0][entry]['query']
			title[entry] = fileContent[0][entry]['title']

		# process time of grammar of submissions of a user
		gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)	
		submissions = gdb.query("""MATCH (n:`User`)-[:submits]->(s:`Submission`) WHERE HAS (n.username) AND n.username =  '""" + request.GET.get('user') + """' RETURN s""")			
		
		# get the current time
		unix = datetime(1970,1,1)
									
		# get the accuray per smyth key
		for sub in submissions.elements:
			
			if len(sub[0]['data']['smyth']) == 0:
				return self.error_response(request, {'error': 'Smyth keys are necessary for calculating averaged lesson progress.'}, response_class=HttpBadRequest)
			
			t=sub[0]['data']['timestamp']
			t=t[:len(t)-5]
			t=dateutil.parser.parse(t.replace('T', ' '))
			diff = (t-unix).total_seconds()																			
			try:					
				time[sub[0]['data']['smyth']].append(diff)  
			except KeyError as k:
				time[sub[0]['data']['smyth']] = []
				time[sub[0]['data']['smyth']].append(diff)
		
		# calculate the averages and sort by it
		average = {}
		for smyth in time.keys():
			average[smyth] = 0.0
			for value in time[smyth]:
				average[smyth] = average[smyth] + value
				
			av = average[smyth]/len(time[smyth])
			av = datetime.fromtimestamp(int(av)).strftime('%Y-%m-%d %H:%M:%S')
			av = av.replace(' ', 'T')
			average[smyth] = av
		
		sorted_dict = sorted(average.iteritems(), key=operator.itemgetter(1))
		#sorted_reverse = sorted_dict.reverse()
				
		for entry in sorted_dict:
			data['time_ranking'].append({'smyth': entry[0], 'average': average[entry[0]], 'title': title[entry[0]], 'query': query[entry[0]]})
	
		#return the json
		return self.create_response(request, data)
	
	


	
