from __future__ import unicode_literals
# coding: utf8
from django.core.management import setup_environ
from phaidra import settings
from tastypie.bundle import Bundle
from django.contrib.webdesign.lorem_ipsum import sentence
setup_environ(settings)
from django.conf.urls import url
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import Http404
from django.middleware.csrf import _get_new_csrf_key as get_new_csrf_key
from django.middleware.csrf import _sanitize_token, constant_time_compare

from app.models import Slide, Submission, AppUser, Document, Sentence, Word, Lemma

from tastypie import fields
from tastypie.authentication import BasicAuthentication, SessionAuthentication, MultiAuthentication, Authentication
from tastypie.authorization import Authorization, ReadOnlyAuthorization
from tastypie.exceptions import Unauthorized
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.utils import trailing_slash
from tastypie.http import HttpUnauthorized, HttpForbidden, HttpBadRequest

import os
import json
import random
from random import shuffle
from neo4django.db.models import NodeModel

import time

class UserObjectsOnlyAuthorization(Authorization):
	def read_list(self, object_list, bundle):
		user_pk = bundle.request.user.pk
		return object_list.filter(user=user_pk)
	
	def read_detail(self, object_list, bundle):
		return bundle.obj.user == bundle.request.user
	
	def create_list(self, object_list, bundle):
		return object_list

	def create_detail(self, object_list, bundle):
		return bundle.obj.user == bundle.request.user

	def update_list(self, object_list, bundle):
		allowed = []

		for obj in object_list:
			if obj.user == bundle.request.user:
				allowed.append(obj)

		return allowed
	
	def update_detail(self, object_list, bundle):
		return bundle.obj.user == bundle.request.user.pk
	
	def delete_list(self, object_list, bundle):
		raise Unauthorized("Deletion forbidden")
	
	def delete_detail(self, object_list, bundle):
		raise Unauthorized("Deletion forbidden")

class UserResource(ModelResource):
	class Meta:
		queryset = AppUser.objects.all()
		resource_name = 'user'
		fields = ['first_name', 'last_name', 'username', 'email', 'is_staff']
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
		
		data = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))

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

	def post_list(self, request, **kwargs):
		"""
		Make sure the user isn't already registered, create the user, return user object as JSON.
		"""
		self.method_check(request, allowed=['post'])
		data = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))

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
				'error': e
			})

		return self.create_response(request, {
			'success': True
		})


	def read_list(self, object_list, bundle):
		"""
		Allow the endpoint for the User Resource to display only the logged in user's information
		"""
		self.is_authenticated(request)
		return object_list.filter(pk=bundle.request.user.id)

	def patch_detail(self, request, **kwargs):
		"""
		Update the fields of a user and return the updated User Resource.	
		"""
		try:
			node = AppUser.objects.select_related(depth=1).get(id=kwargs["pk"])
		except ObjectDoesNotExist:
			raise Http404("Cannot find user.")

		body = json.loads(request.body) if type(request.body) is str else request.body
		data = body.copy()

		restricted_fields = ['is_staff', 'is_user', 'username', 'password']

		for field in body:
			if hasattr(node, field) and not field.startswith("_"):
				attr = getattr(node, field)
				value = data[field]

				# Do not alter relationship fields from this endpoint
				if not hasattr(attr, "_rel") and field not in restricted_fields:
					setattr(node, field, value)
				else:
					return self.create_response(request, {
						'success': False,
						'error_message': 'You are not authorized to update this field.'
					})
				continue

			# This field is not contained in our model, so discard it
			del data[field]

		if len(data) > 0:
			node.save()

		# Returns all field data of the related user as response data
		data = {}		
		for property_name in node.property_names(): 		
			data[property_name] = getattr(node, property_name)

		return self.create_response(request, data)


class SlideResource(ModelResource):
	class Meta:
		allowed_methods = ['post', 'get', 'patch']
		always_return_data = True
		authentication = SessionAuthentication()
		#authentication = BasicAuthentication()
		authorization = Authorization()
		excludes = ['answers', 'require_order', 'require_all_answers']
		queryset = Slide.objects.all()
		resource_name = 'slide'

class SubmissionResource(ModelResource):
	class Meta:
		allowed_methods = ['post', 'get', 'patch']
		always_return_data = True
		authentication = SessionAuthentication() 
		#authentication = BasicAuthentication()
		authorization = UserObjectsOnlyAuthorization()
		excludes = ['require_order', 'require_all']
		queryset = Submission.objects.all()
		resource_name = 'submission'

	# This cannot be the best way of doing this, but deadlines are looming. 
	# For a cleaner implementation, see: https://github.com/jplusplus/detective.io/blob/master/app/detective/individual.py
		
	def post_list(self, request, **kwargs):
		"""
		Create a new submission object, which relates to the slide it responds to and the user who submitted it.
		Return the submission object, complete with whether or not they got the answer correct.
		"""
		self.method_check(request, allowed=['post'])
		self.is_authenticated(request)

		if not request.user or not request.user.is_authenticated():
			return self.create_response(request, { 'success': False, 'error_message': 'You are not authenticated, %s' % request.user })

		data = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))

		# Get the slide node that the user is answering before creation of the submission -- this also needs further checks (e.g. can they even submit to this slide yet?)
		#try:
		#	slide_node = Slide.objects.get(pk=data.get("slide"))
		#except ObjectDoesNotExist as e:
		#	return self.create_response(request, {
		#		'success': False,
		#		'error': e
		#	})

		# Ensuring that the user is who s/he says s/he is, handled by user objs. auth.
		try:
			user_node = AppUser.objects.get(username=data.get("user"))
		except ObjectDoesNotExist as e:
			# Is it possible this could occur if the user passes authentication?
			return self.create_response(request, {
				'success': False,
				'error': e
			})

		# some validation in the manager class of the model
		# on errors which are not caught in the manager class, the node will still be created because save is called (too?) soon
		# look into django.db.models.Model save method for saving behaviour on error?!
		node = Submission.objects.create(
			response = data.get("response"), # string array
			tasktags = data.get("tasktags"), # string array
			speed = int(data.get("speed")),		 # integer
			accuracy = int(data.get("accuracy")), # integer
			encounteredWords = data.get("encounteredWords"), # string array
			slideType = data.get("slideType"), # string
			timestamp = data.get("timestamp") # datetime
		)
		if node is None :
			# in case an error wasn't already raised 			
			raise ValidationError('Submission node could not be created.')
	
		# Form the connections from the new Submission node to the existing slide and user nodes
		#node.slide = slide_node
		node.user = user_node

		# create the body
		body = json.loads(request.body) if type(request.body) is str else request.body
		# data = body.clone()

		# Check to see if the user answered the question correctly or not
		node.save()

		return self.create_response(request, body)


class VisualizationResource(ModelResource):
							
	class Meta:
		queryset = Word.objects.all()
		resource_name = 'visualization'
		#always_return_data = True
		#excludes = ['require_order', 'require_all']
		authorization = ReadOnlyAuthorization()

	def prepend_urls(self, *args, **kwargs):	
		
		return [
			url(r"^(?P<resource_name>%s)/%s%s$" % (self._meta.resource_name, 'encountered', trailing_slash()), self.wrap_view('encountered'), name="api_%s" % 'encountered')
			]

	#/api/visualization/encountered/?format=json&level=word-level&range=urn:cts:greekLit:tlg0003.tlg001.perseus-grc1:1.108.5:5-7&user=john
	def encountered(self, request, **kwargs):
		
		"""
		Start visualization...
		"""
		query_params = {}
		for obj in request.GET.keys():
			if obj in dir(Word) and request.GET.get(obj) is not None:
				query_params[obj] = request.GET.get(obj)
		
		user = AppUser.objects.get(username = request.GET.get('user'))
		# calculate CTSs of the word range (later look them up within submissions of the user)
		# preparation
		ctsArray = []
		cts = request.GET.get('range')			 					
		#rangeArray = cts.split(':')
		# get the stem
		endIndex = len(cts)-len(cts.split(':')[len(cts.split(':'))-1])
		rangeStem = cts[0:endIndex]
		
		# get the numbers
		numbersArray = cts.split(':')[len(cts.split(':'))-1].split('-')
		for num in range(int(numbersArray[0]), int(numbersArray[1])+1):
			ctsArray.append(rangeStem + str(num))
			
		# get the morph intersected info to the words via submissions of a user and a file...
		for sub in user.submissions.all():
			# get the file entry:
			with open('../static/js/smyth.json', 'r') as json_data:
				d = json.load(json_data)
				json_data.close()
			
		return self.create_response(request, d)
		
		#for word in words:
		#	sentence = word.sentence
		#	# asap check if the short sentence to a word's sentence returns a set with query params matching words
		#	sentence = sentence.get_shortened(query_params)
		#	if sentence is not None:
		#
		#		data = {}
		#		data['words'] = []
		#		for word in sentence:
		#			w = word.__dict__
		#			data['words'].append(w['_prop_values'])
		#								
		#		return self.create_response(request, data)
		
		return self.error_response(request, {'error': 'No short sentences hit your query.'}, response_class=HttpBadRequest)	



class DocumentResource(ModelResource):
	
	#document/?format=json&sentences__length=24
	sentences = fields.ToManyField('api.api.SentenceResource', lambda bundle: Sentence.objects.filter(document__name = bundle.obj.name), null = True, blank = True )# full = True)
							
	class Meta:
		queryset = Document.objects.all()
		resource_name = 'document'
		always_return_data = True
		excludes = ['require_order', 'require_all']
		authorization = ReadOnlyAuthorization()
		filtering = {'internal': ALL,
					'CTS': ALL,
					'author': ALL,
					'name': ALL,
					'name_eng': ALL,
					'lang': ALL,
					'sentences': ALL_WITH_RELATIONS}


class SentenceResource(ModelResource):
	#sentence/?format=json&file__lang=fas
	file = fields.ForeignKey(DocumentResource, 'document')
	# expensive
	words = fields.ToManyField('api.api.WordResource', lambda bundle: Word.objects.filter(sentence__sentence=bundle.obj.sentence), null=True, blank=True, full = True)
		
	class Meta:
		queryset = Sentence.objects.all()
		resource_name = 'sentence'
		always_return_data = True
		excludes = ['require_order', 'require_all']
		authorization = ReadOnlyAuthorization()
		filtering = {'internal': ALL,
					'CTS': ALL,
					'length': ALL,
					'file': ALL_WITH_RELATIONS,
					'words': ALL_WITH_RELATIONS}
		limit = 5	
		
	"""
	Gets one or more short/long randomized/not random sentence(s) with provided morphological information to one word.
	Makes sure the query params are still supported by the short sentence.
	"""
	def get_list(self, request, **kwargs):
		
		query_params = {}
		for obj in request.GET.keys():
			if obj in dir(Word) and request.GET.get(obj) is not None:
				query_params[obj] = request.GET.get(obj)
			elif obj.split('__')[0] in dir(Word) and request.GET.get(obj) is not None:
				query_params[obj] = request.GET.get(obj)
		
		# filter on parameters 						
		words = Word.objects.filter(**query_params)
		
		if len(words) < 1:
			return self.error_response(request, {'error': 'No sentences hit your query.'}, response_class=HttpBadRequest)	
		
		data = {}
		data['sentences'] = []
				
		# if ordinary filter behavior is required, put key default
		if 'default' in request.GET.keys():		
			return super(SentenceResource, self).get_list(request, **kwargs)
		
		#/api/sentence/?randomized=&short=&format=json&lemma=κρατέω
		elif 'randomized' in request.GET.keys():
						
			if 'short' in request.GET.keys():
				
				# make this hack only for randomized/short for performance improvement; run over sentences instead of words
				if len(query_params) < 1:
					
					x = list(Sentence.objects.all())
					sentences = sorted(x, key=lambda *args: random.random())
				
					for sentence in sentences:
						sentence = sentence.get_shortened(query_params)
						# asap check if the short sentence to a word's sentence returns a set with query params matching words
						if sentence is not None:
							
							tmp = {}
							tmp['words'] = []
							for word in sentence:
								w = word.__dict__
								tmp['words'].append(w['_prop_values'])
								
							data['sentences'].append(tmp)												
							return self.create_response(request, data)
						
					return self.error_response(request, {'error': 'No short sentences hit your query.'}, response_class=HttpBadRequest)
					
				else:
					
					x = list(words)
					words = sorted(x, key=lambda *args: random.random())
		
					for word in words:
						sentence = word.sentence
						sentence = sentence.get_shortened(query_params)
						# asap check if the short sentence to a word's sentence returns a set with query params matching words
						if sentence is not None:
							
							tmp = {}
							tmp['words'] = []
							for word in sentence:
								w = word.__dict__
								tmp['words'].append(w['_prop_values'])
								
							data['sentences'].append(tmp)														
							return self.create_response(request, data)
						
					return self.error_response(request, {'error': 'No short sentences hit your query.'}, response_class=HttpBadRequest)
			
			# randomized, long
			#/api/sentence/?randomized=&format=json&lemma=κρατέω	
			else:
				
				word = random.choice(words)
				sentence = word.sentence
				
				tmp = {'sentence': sentence.__dict__}
				tmp = tmp['sentence']['_prop_values']
				tmp['words'] = []	
				for word in reversed(sentence.words.all()):			
					w = word.__dict__
					tmp['words'].append(w['_prop_values'])
				
				data['sentences'].append(tmp)
				return self.create_response(request, data)
		
		# not randomized
		else:
			# not randomized, short and CTS queries a sentence via CTS
			if 'short' in request.GET.keys():
				
				CTS = request.GET.get('CTS')
				# if CTS is missed all sentences containing words that hit the query are returned, Expensive!!!
				#/api/sentence/?format=json&short=&form=ἀπέβησαν
				# make it a set	
				if CTS is None:
					
					for word in words:
						sentence = word.sentence
						# asap check if the short sentence to a word's sentence returns a set with query params matching words
						sentence = sentence.get_shortened(query_params)
					
						if sentence is not None:
							tmp = {}
							tmp['words'] = []	
							for word in sentence:
								w = word.__dict__
								tmp['words'].append(w['_prop_values'])
							
							data['sentences'].append(tmp)
							
					return self.create_response(request, data)
				
				# not randomized, short with CTS
				#/api/sentence/?format=json&short=&CTS=urn:cts:greekLit:tlg0003.tlg001.perseus-grc1:1.108.5
				# TODO: object sentence?????
				else:
					sentence = Sentence.objects.get(CTS = CTS)
					sentence = sentence.get_shortened({})
					
					tmp = {}
					tmp['words'] = []				
					for word in sentence:
						w = word.__dict__
						tmp['words'].append(w['_prop_values'])
						
					data['sentences'].append(tmp)					
					return self.create_response(request, data)
				
				return self.error_response(request, {'error': 'No short sentences hit your query.'}, response_class=HttpBadRequest)
			
			# not randomized, long, no CTS implies more than one sentence
			else:
				CTS = request.GET.get('CTS')
				# if CTS is missed all sentences containing words that hit the query are returned
				#/api/sentence/?format=json&form=ἀπέβησαν&lemma__endswith=νω
				if CTS is None:

					for word in words:
						
						sentence = word.sentence
						tmp = {'sentence': sentence.__dict__}
						tmp = tmp['sentence']['_prop_values']
						tmp['words'] = []	
						for word in reversed(sentence.words.all()):
					
							w = word.__dict__
							tmp['words'].append(w['_prop_values'])
							
						data['sentences'].append(tmp)
						
					return self.create_response(request, data)
				
				# not randomized, long, CTS return one sentence
				#/api/sentence/?format=json&CTS=urn:cts:greekLit:tlg0003.tlg001.perseus-grc1:1.108.5
				else:
						
					sentence = Sentence.objects.get(CTS = CTS)
								
					tmp = {'sentence': sentence.__dict__}
					tmp = tmp['sentence']['_prop_values']
					tmp['words'] = []
					for word in reversed(sentence.words.all()):
						
						w = word.__dict__
						tmp['words'].append(w['_prop_values'])
					
					data['sentences'].append(tmp)
					
					return self.create_response(request, data)
				
				return self.error_response(request, {'error': 'No sentences hit your query.'}, response_class=HttpBadRequest)
			
	
	
	def prepend_urls(self, *args, **kwargs):	
		
		return [
			url(r"^(?P<resource_name>%s)/%s%s$" % (self._meta.resource_name, 'get_one_random', trailing_slash()), self.wrap_view('get_one_random'), name="api_%s" % 'get_one_random'),
			url(r"^(?P<resource_name>%s)/%s%s$" % (self._meta.resource_name, 'get_one_random_short', trailing_slash()), self.wrap_view('get_one_random_short'), name="api_%s" % 'get_one_random_short')
			]
	
	#/api/sentence/get_one_random/?format=json&case=gen&lemma=Λακεδαιμόνιος
	def get_one_random(self, request, **kwargs):
		
		"""
		Gets one random sentence of sentences with provided morphological information to one word.
		"""
		length = request.GET.get('length')
		query_params = {}
		for obj in request.GET.keys():
			if obj in dir(Word) and request.GET.get(obj) is not None:
				query_params[obj] = request.GET.get(obj)
							
		words = Word.objects.filter(**query_params)
		if len(words) < 1:
			return self.error_response(request, {'error': 'No results hit this query.'}, response_class=HttpBadRequest)
		
		if length is not None:
			
			sentences = []
			for w in words:
				if (w.sentence.length<=int(length)):
					sentences.append(w.sentence)
			
			if len(sentences) < 1: return self.error_response(request, {'error': 'Wanna try it without sentence length condition?'}, response_class=HttpBadRequest)
		
			sentence = random.choice(sentences)
		
		else : 
			word = random.choice(words)
			sentence = word.sentence
		
		#data = self.build_bundle(obj=sentence, request=request)
		#data = self.full_dehydrate(data)
			
		data = {'sentence': sentence.__dict__}
		data = data['sentence']['_prop_values']
		data['words'] = []			
		for word in reversed(sentence.words.all()) :
			w = word.__dict__
			data['words'].append(w['_prop_values'])
										
		return self.create_response(request, data)	
		#return self.error_response(request, {'error': 'lemma and case are required.'}, response_class=HttpBadRequest)
		
	#/api/sentence/get_one_random_short/?format=json&case=gen&lemma=Λακεδαιμόνιος κρατέω
	def get_one_random_short(self, request, **kwargs):
		
		"""
		Gets one short random sentence of sentences with provided morphological information to one word.
		Makes sure the query params are still supported by the short sentence
		"""
		#query_params = {'case': 'gen', 'lemma': 'Λακεδαιμόνιος'}
		query_params = {}
		for obj in request.GET.keys():
			if obj in dir(Word) and request.GET.get(obj) is not None:
				query_params[obj] = request.GET.get(obj)
		
		# filter on params asap brings kinda performance, shuffle result set 						
		x = list(Word.objects.filter(**query_params))
		words = sorted(x, key=lambda *args: random.random())
		
		for word in words:
			sentence = word.sentence
			# asap check if the short sentence to a word's sentence returns a set with query params matching words
			sentence = sentence.get_shortened(query_params)
			if sentence is not None:
		
				data = {}
				data['words'] = []
				for word in sentence:
					w = word.__dict__
					data['words'].append(w['_prop_values'])
										
				return self.create_response(request, data)
		
		return self.error_response(request, {'error': 'No short sentences hit your query.'}, response_class=HttpBadRequest)
	
 		
class SentenceShortResource(ModelResource):
	"""
	Test resource for short sentence to parameter returns.
	"""
	file = fields.ForeignKey(DocumentResource, 'document')
	# expensive
	words = fields.ToManyField('api.api.WordResource', lambda bundle: Word.objects.filter(sentence__sentence=bundle.obj.sentence), null=True, blank=True)#, full = True)
		
	class Meta:
		queryset = Sentence.objects.filter()
		resource_name = 'sentence/short'
		always_return_data = True
		excludes = ['require_order', 'require_all', 'sentence']
		authorization = ReadOnlyAuthorization()
		filtering = {'internal': ALL,
					'CTS': ALL,
					'length': ALL,
					'file': ALL_WITH_RELATIONS,
					'words': ALL_WITH_RELATIONS}
		limit = 3
	
	def prepend_urls(self, *args, **kwargs):	
		
		return [
			url(r"^(?P<resource_name>%s)/%s%s$" % (self._meta.resource_name, 'get_one_random', trailing_slash()), self.wrap_view('get_one_random'), name="api_%s" % 'get_one_random'),
			]

	#/api/sentence/short/get_one_random/?format=json&lemma=Λακεδαιμόνιος
	#/api/sentence/short/get_one_random/?format=json&lemmaEnd=γος
	def get_one_random(self, request, **kwargs):
		
		"""
		Gets one random sentence of sentences with provided morphological information to one word.
		Makes sure the query params are still supported by the short sentence.
		"""
		#query_params = {'case': 'gen', 'lemma': 'Λακεδαιμόνιος'}
		query_params = {}
		for obj in request.GET.keys():
			if obj in dir(Word) and request.GET.get(obj) is not None:
				query_params[obj] = request.GET.get(obj)
		
		# filter on params asap brings kinda performance, shuffle result set 						
		#x = list(Word.objects.filter(**query_params))
		x = list(Word.objects.filter(lemma__ENDSWITH = request.GET.get('lemmaEnd')))
		words = sorted(x, key=lambda *args: random.random())
		
		for word in words:
			sentence = word.sentence
			# asap check if the short sentence to a word's sentence returns a set with query params matching words
			sentence = sentence.get_shortened(query_params)
			if sentence is not None:
		
				data = {}
				data['words'] = []
				for word in sentence:
					w = word.__dict__
					data['words'].append(w['_prop_values'])
										
				return self.create_response(request, data)
		
		return self.error_response(request, {'error': 'No short sentences hit your query.'}, response_class=HttpBadRequest)	
	
		
class LemmaResource(ModelResource):
	
	# filtering on word object list is faster than on the bundle object; expensive anyway
	words = fields.ToManyField('api.api.WordResource', lambda bundle: Word.objects.filter(lemma=bundle.obj), null=True, blank=True)
	
	class Meta:
		queryset = Lemma.objects.all()
		resource_name = 'lemma'
		always_return_data = True
		excludes = ['require_order', 'require_all']
		authorization = ReadOnlyAuthorization()
		filtering = {'value': ALL,
					#'wordcount': ALL, # coming soon?
					'words': ALL_WITH_RELATIONS}


class LemmaWordResource(ModelResource):

	"""
	Returns a list of lemmas with special properties of a relative - words.
	"""
	words = fields.ToManyField('api.api.WordResource', lambda bundle: Word.objects.filter(lemma=bundle.obj), null=True, blank=True) 
	
	class Meta:
		queryset = Lemma.objects.all()
		resource_name = 'lemma/word'
		always_return_data = True
		excludes = ['require_order', 'require_all']
		authorization = ReadOnlyAuthorization()
		filtering = {'value': ALL}

	def obj_get_list(self, bundle, **kwargs):
		if 'word_number' in bundle.request.GET.keys() and 'posAdd' in bundle.request.GET.keys():
			data = []
			words = Word.objects.all()
			## localhost:8000/api/lemma/word/?word_number=2&pos=verb&posAdd=o_stem&format=json
			if 'pos' in bundle.request.GET.keys() :
				words = Word.objects.filter(pos=bundle.request.GET['pos'])
			if 'posAdd' in bundle.request.GET.keys() :
				words = words.filter(posAdd__contains=bundle.request.GET['posAdd'])
			for word in reversed(words):
				if word.lemmas is not None and word.lemmas.valuesCount() >= int(bundle.request.GET['word_number']) :
					data.append(word.lemmas)
			if len(data) >= 1:
				return data
		return super(LemmaWordResource, self).obj_get_list(bundle, **kwargs).filter()


class TranslationResource(ModelResource):
	
	#sentenceRes = fields.ForeignKey(SentenceResource, 'sentence')#, full = True	
		
	class Meta:
		queryset = Word.objects.all()
		resource_name = 'translation'
		always_return_data = True
		excludes = ['require_all', 'sentence', 'case', 'cid', 'degree', 'dialect', 'form', 'gender', 'head', 'isIndecl', 
				'lemma', 'lemmas', 'mood', 'number' , 'person', 'pos', 'posAdd', 'posClass', 'ref', 'relation', 'tbwid', 'tense', 'translation', 'voice']		
		authorization = ReadOnlyAuthorization()
		filtering = {'internal': ALL,
					'CTS': ALL,
					'value': ALL,
					'length': ALL,					
					'sentenceRes': ALL_WITH_RELATIONS}


class WordResource(ModelResource):

	##base = fields.ToOneField('api.api.LemmaResource', lambda bundle: None if bundle.obj.lemmas is None else '' if bundle.obj.lemmas is '' else Lemma.objects.get(value=bundle.obj.lemmas), null=True, blank=True) 
	
	#word/?format=json&sentenceRes__file__lang=fas
	#sentenceRes = fields.ForeignKey(SentenceResource, 'sentence')#, full = True)
	#root = fields.ToOneField('api.api.LemmaResource', lambda bundle: None if bundle.obj.lemmas is None else Lemma.objects.get(value=bundle.obj.lemmas), null=True, blank=True)			
	
	#translation = fields.ToManyField('api.api.TranslationResource', attribute=lambda bundle: bundle.obj.translation.all(), null=True, blank=True)

	class Meta:
		queryset = Word.objects.all()
		resource_name = 'word'
		always_return_data = True
		excludes = ['require_all', 'sentence', 'children']
		authorization = ReadOnlyAuthorization()
		filtering = {'internal': ALL,
					'CTS': ALL,
					'value': ALL,
					'length': ALL,
					'form': ALL,
					'lemma': ALL,
					'pos': ALL, 
					'person': ALL,
					'number': ALL,
					'tense': ALL,
					'mood': ALL,
					'voice': ALL,
					'gender': ALL,
					'case': ALL,
					'degree': ALL,
					'dialect': ALL,
					'isIndecl': ALL,
					'posAdd': ALL,					
					'sentenceRes': ALL_WITH_RELATIONS,
					'base': ALL_WITH_RELATIONS}
		
	def build_filters(self, filters=None):
		"""
		A filter example to compose several conditions within a filer - this would make sense if we ask for a special (static) compos. more often
		this should MAYBE be more generic! 
		"""
		if filters is None:
			filters = {}
				 		
	 	orm_filters = super(WordResource, self).build_filters(filters)
	 	
	 	if 'q' in filters:
			#/api/word/?q=perseus-grc1
			orm_filters = {'CTS__contains':filters['q'], # comes from the url: dyn; contains greek words, that are masc. nouns
						'pos': "noun",
						'gender': "masc"}
		return orm_filters
			
		
					
	
	
	
	
