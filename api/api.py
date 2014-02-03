from __future__ import unicode_literals
# coding: utf8
from django.core.management import setup_environ
from phaidra import settings
from tastypie.bundle import Bundle
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
from tastypie.http import HttpUnauthorized, HttpForbidden

import json
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
	
	#sents = fields.ToManyField('app.api.SentenceResource', 'file', full=True, null = True, blank = True)
	# doesnt work yet
	sents = fields.ToManyField('api.api.SentenceResource', lambda bundle: Sentence.objects.filter(document_name = bundle.obj.name ), full = True, null = True, blank = True )#full=True)
							
	class Meta:
		queryset = Document.objects.all()
		resource_name = 'document'
		always_return_data = True
		excludes = ['require_order', 'require_all']
		authorization = ReadOnlyAuthorization()
		filtering = {'CTS': ALL,
					'lang': ALL,
					#'sent': ALL_WITH_RELATIONS
					}


class SentenceResource(ModelResource):
	
	file = fields.ForeignKey(DocumentResource, 'document')
	
	class Meta:
		queryset = Sentence.objects.all()
		resource_name = 'sentence'
		always_return_data = True
		excludes = ['require_order', 'require_all']
		authorization = ReadOnlyAuthorization()
		filtering = {'CTS': ALL
					}
		#limit=2
 	
class LemmaResource(ModelResource):
	
	# this works because Lemma object unicode function equals the lemma attribute of the word model
	words = fields.ToManyField('api.api.WordResource', lambda bundle: Word.objects.filter(lemma=bundle.obj))
	
	class Meta:
		queryset = Lemma.objects.all()
		resource_name = 'lemma'
		always_return_data = True
		excludes = ['require_order', 'require_all']
		authorization = ReadOnlyAuthorization()
		filtering = {'value': ALL}
		#limit = 50

class LemmaWordResource(ModelResource):

	# filter(lemma=bundle.obj.lemma))
	words = fields.ToManyField('api.api.WordResource', lambda bundle: Word.objects.filter(lemma=bundle.obj)) 
	class Meta:
		# merges with the return of obj_get_list
		queryset = Lemma.objects.all()
		resource_name = 'lemma/word'
		always_return_data = True
		excludes = ['require_order', 'require_all']
		authorization = ReadOnlyAuthorization()
		filtering = {'value': ALL}
		limit = 100

	def obj_get_list(self, bundle, **kwargs):
		if ('pos' and 'posAdd') in bundle.request.GET.keys():
			data = []
			## http://localhost:8000/api/lemma/word/?pos=verb&posAdd=o_stem&format=json
			words = Word.objects.filter(pos=bundle.request.GET['pos'], posAdd__contains = bundle.request.GET['posAdd'] )
			for word in words:
				# catch target language words without w/o lemma!!
				if word.lemmas is not None and word.lemmas.valuesCount() >= 2:
					data.append(word.lemmas)
			return data	
		return super(LemmaWordResource, self).obj_get_list(bundle, **kwargs).filter()
		##return super(WordResource, self).obj_get_list(bundle, **kwargs).filter(CTS=bundle.request.GET['CTS'])		
	
	#def dehydrate_value(self, bundle):
		#return unicode(bundle.obj.lemma) or u''  


class WordResource(ModelResource):
	
	# doesnt work for detail words with relations
	base = fields.ToOneField('api.api.LemmaResource', lambda bundle: None if bundle.obj.lemmas is None else '' if bundle.obj.lemmas is '' else Lemma.objects.get(value=bundle.obj.lemmas), full = True, null=True, blank=True) 
	  
	class Meta:
		queryset = Word.objects.all()
		resource_name = 'word'
		always_return_data = True
		excludes = ['require_order', 'require_all']
		authorization = ReadOnlyAuthorization()
		filtering = {'CTS': ALL,
					'pos': ALL, 
					'gender': ALL}
		limit = 5
		
	def build_filters(self, filters=None):
		"""
		a filter example to compose several conditions within a filer
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
			
		
					
	
	
	
	