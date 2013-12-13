from django.conf.urls import url
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import Http404
from django.middleware.csrf import _get_new_csrf_key as get_new_csrf_key

from app.models import Slide, Submission, AppUser

from tastypie.authentication import BasicAuthentication, SessionAuthentication, MultiAuthentication, Authentication
from tastypie.authorization import Authorization, ReadOnlyAuthorization
from tastypie.exceptions import Unauthorized
from tastypie.models import create_api_key
from tastypie.resources import ModelResource
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

	def post_list(self, object_list, bundle):
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

		# We need to fill out the entire response so the API is round-trippable before returning the response
		return self.create_response(request, data)

class SlideResource(ModelResource):
	class Meta:
		allowed_methods = ['post', 'get', 'patch']
		always_return_data = True
		authentication = SessionAuthentication() 
		authorization = Authorization()
		excludes = ['answers', 'require_order', 'require_all_answers']
		queryset = Slide.objects.all()
		resource_name = 'slide'

class SubmissionResource(ModelResource):
	class Meta:
		allowed_methods = ['post', 'get', 'patch']
		always_return_data = True
		authentication = SessionAuthentication() 
		authorization = Authorization()
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
		# on errors which are not caught in the manager class, the node will still be created (try except wouldn't work as well)
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
