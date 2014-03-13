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

import json
import random
from neo4django.db.models import NodeModel

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
		try:
			slide_node = Slide.objects.get(pk=data.get("slide"))
		except ObjectDoesNotExist as e:
			return self.create_response(request, {
				'success': False,
				'error': e
			})

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
			value = data.get("value"),
			started = data.get("started"),
			finished = data.get("finished")
		)
		if node is None :
			# in case an error wasn't already raised 			
			raise ValidationError('Something went wrong with the submission creation.')
	
		# Form the connections from the new Submission node to the existing slide and user nodes
		node.slide = slide_node
		node.user = user_node

		# create the body
		body = json.loads(request.body) if type(request.body) is str else request.body
		# data = body.clone()

		# Check to see if the user answered the question correctly or not
		node.save()

		return self.create_response(request, body)



class DocumentResource(ModelResource):
	
	# foreign key to sentences of a document
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
	file = fields.ForeignKey(DocumentResource, 'document')#full = True)
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
		
		
	def prepend_urls(self, *args, **kwargs):
		
		name = 'get_one_random'
		return [url(r"^(?P<resource_name>%s)/%s%s$" % (self._meta.resource_name, name, trailing_slash()), self.wrap_view(name), name="api_%s" % name)]

	
	def get_one_random(self, request, **kwargs):
		
		"""
		Gets one random sentence of sentences with provided morphological information to one word.
		"""
		case = request.GET.get('case')
		lemma = request.GET.get('lemma')
		number = request.GET.get('number')
		length = request.GET.get('length')
		posAdd = request.GET.get('posAdd')
		tense = request.GET.get('tense')
		voice = request.GET.get('voice')
		mood = request.GET.get('mood')
		query_params = {}
				
		if case is not None:
			query_params['case'] = case
			
		if lemma is not None:
			#query_params = {'case': case, 'lemma': lemma}
			query_params['lemma'] = lemma
			
		if number is not None:
			query_params['number'] = number

		if tense is not None:
			query_params['tense'] = tense

		if voice is not None:
			query_params['voice'] = voice

		if mood is not None:
			query_params['mood'] = mood
			
		if posAdd is not None:
			query_params['posAdd__contains'] = posAdd
			
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
			
		data = {'sentence': sentence.__dict__}
		data = data['sentence']['_prop_values']
		data['words'] = []			
		for word in reversed(sentence.words.all()) :
			w = word.__dict__
			data['words'].append(w['_prop_values'])
										
		return self.create_response(request, data)	
		#return self.error_response(request, {'error': 'lemma and case are required.'}, response_class=HttpBadRequest)
		
 		
class SentenceRandomResource(ModelResource):
	
	"""
	This resource searches a related object to given object parameters and
	returns the selected bundled and dehydrated as in a detail view. It is far more expensive than working with the __dict__ of an object.
	"""
	file = fields.ForeignKey(DocumentResource, 'document')#full = True)
	# expensive
	words = fields.ToManyField('api.api.WordResource', lambda bundle: Word.objects.filter(sentence__sentence=bundle.obj.sentence), null=True, blank=True)#, full = True)
		
	class Meta:
		queryset = Sentence.objects.filter()
		resource_name = 'sentence/random'
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
		
		name = 'get_one_random'
		return [url(r"^(?P<resource_name>%s)/%s%s$" % (self._meta.resource_name, name, trailing_slash()), self.wrap_view(name), name="api_%s" % name)]

	
	def get_one_random(self, request, **kwargs):
		
		"""
		Gets one random sentence of sentences with provided `case` and `lemma` params.
		"""
		case = request.GET.get('case')
		lemma = request.GET.get('lemma')
		number = request.GET.get('number')
		
		if case and lemma:
			
			query_params = {'case': case, 'lemma': lemma}
			if number is not None:
				
				query_params['number'] = number
				words = Word.objects.filter(**query_params)
				word = random.choice(words)
				sentence = word.sentence
			
				data = {'sentence': word.sentence.__dict__}
				data = data['sentence']['_prop_values']
				data['words'] = []			
				for word in sentence.words.all() :
					w = word.__dict__
					data['words'].append(w['_prop_values'])
										
			return self.create_response(request, data)
		
		else:
			return self.error_response(request, {'error': 'lemma and case are required.'}, response_class=HttpBadRequest)
		
		
class LemmaResource(ModelResource):
	
	# filtering on word object list is faster than on the bundle object; expensive anyway
	words = fields.ToManyField('api.api.WordResource', lambda bundle: Word.objects.filter(lemma=bundle.obj))
	
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
	# field makes the resource view slower
	words = fields.ToManyField('api.api.WordResource', lambda bundle: Word.objects.filter(lemma=bundle.obj)) 
	
	class Meta:
		queryset = Lemma.objects.all()	# merges with the return of obj_get_list
		resource_name = 'lemma/word'
		always_return_data = True
		excludes = ['require_order', 'require_all']
		authorization = ReadOnlyAuthorization()
		filtering = {'value': ALL}

	def obj_get_list(self, bundle, **kwargs):
		if 'word_number' in bundle.request.GET.keys() and 'posAdd' in bundle.request.GET.keys():
			data = []
			words = Word.objects.all()
			## http://localhost:8000/api/lemma/word/?word_number=2&pos=verb&posAdd=o_stem&format=json
			if 'pos' in bundle.request.GET.keys() :
				words = Word.objects.filter(pos=bundle.request.GET['pos'])
			if 'posAdd' in bundle.request.GET.keys() :
				words = words.filter(posAdd__contains=bundle.request.GET['posAdd'])
			for word in words:
				if word.lemmas is not None and word.lemmas.valuesCount() >= int(bundle.request.GET['word_number']) :
					data.append(word.lemmas)
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

	#base = fields.ToOneField('api.api.LemmaResource', lambda bundle: None if bundle.obj.lemmas is None else '' if bundle.obj.lemmas is '' else Lemma.objects.get(value=bundle.obj.lemmas), null=True, blank=True) 
	#word/?format=json&sentenceRes__file__lang=fas
	#sentenceRes = fields.ForeignKey(SentenceResource, 'sentence')#, full = True)
	
	#root = fields.ToOneField('api.api.LemmaResource', lambda bundle: None if bundle.obj.lemmas is None else Lemma.objects.get(value=bundle.obj.lemmas), null=True, blank=True)			
	#word/?format=json&sentenceRes__file__lang=fas
	#translation = fields.ToManyField('api.api.TranslationResource', attribute=lambda bundle: bundle.obj.translation.all(), full=True, null=True, blank=True)

	class Meta:
		queryset = Word.objects.all()
		resource_name = 'word'
		always_return_data = True
		excludes = ['require_all', 'sentence']
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
			
		
					
	
	
	
	
