from django.db import IntegrityError
from django.conf.urls import url
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import _get_new_csrf_key as get_new_csrf_key

from tastypie import fields
from tastypie.authentication import SessionAuthentication, BasicAuthentication, Authentication
from tastypie.authorization import Authorization
from tastypie.utils import trailing_slash
from tastypie.http import HttpUnauthorized, HttpForbidden, HttpConflict
from tastypie.exceptions import BadRequest
from tastypie.resources import ModelResource

import json

from app.models import AppUser

from validation import ResourceValidation
from utils import DataObject

class CreateUserResource(ModelResource):
	
	class Meta:
		queryset = AppUser.objects.all()
		resource_name = 'create_user'
		fields = ['username', 'first_name', 'last_name', 'last_login']
		allowed_methods = ['post']
		always_return_data = True
		authentication = Authentication()
		authorization = Authorization()
		validation =  ResourceValidation()
		
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
			return self.error_response(request, {
				'error': e,
				'error_message': 'Username already in use.',
				'success': False,
			}, response_class=HttpConflict)
		
		body = json.loads(request.body) if type(request.body) is str else request.body
				
		return self.create_response(request, body)
		
						
class UserResource(ModelResource):
	class Meta:
		queryset = AppUser.objects.all()
		resource_name = 'user'
		fields = ['username', 'first_name', 'last_name', 'last_login', 'lang', 'readingCTS']
		allowed_methods = ['get', 'post', 'patch']
		always_return_data = True
		authentication = SessionAuthentication()
		authorization = Authorization()
		validation =  ResourceValidation()

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
				return self.error_response(request, {
					'success': False,
					'reason': 'disabled',
				}, response_class=HttpForbidden)
		else:				
			return self.error_response(request, {
				'error_message': 'Incorrect username or password.',
				'success': False,
			}, response_class=HttpUnauthorized)

			
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
	
	def obj_get_list(self, bundle, **kwargs):
		
		try:
			return [bundle.request.user]
			#return self.authorized_read_list(bundle.request, bundle)
		except ValueError:
			raise BadRequest("Invalid resource lookup data provided (mismatched type).")
	
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
