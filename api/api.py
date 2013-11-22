from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import Http404

from core.models.slide import Slide
from core.models.submission import Submission
from core.models.user import AppUser

from tastypie.authentication import BasicAuthentication, SessionAuthentication, MultiAuthentication, Authentication
from tastypie.authorization import Authorization, ReadOnlyAuthorization
from tastypie.exceptions import Unauthorized
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer
from tastypie.utils import trailing_slash

import json
from neo4django.db.models import NodeModel

class UserObjectsOnlyAuthorization(Authorization):
	def read_list(self, object_list, bundle):
		user_pk = bundle.request.user.pk
		return object_list.filter(user=user_pk)
	
	def read_detail(self, object_list, bundle):
		return bundle.obj.user == bundle.request.user.pk
	
	def create_list(self, object_list, bundle):
		return object_list

	def create_detail(self, object_list, bundle):
		return bundle.obj.user == bundle.request.user.pk

	def update_list(self, object_list, bundle):
		allowed = []

		for obj in object_list:
			if obj.user == bundle.request.user.pk:
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
		fields = ['first_name', 'last_name', 'username', 'email', 'is_staff', 'password']
		allowed_methods = ['get']
		always_return_data = True

class SlideResource(ModelResource):
	class Meta:
		queryset = Slide.objects.all()
		resource_name = 'slide'
		excludes = ['answers', 'require_order', 'require_all']
		always_return_data = True

class SubmissionResource(ModelResource):
	class Meta:
		queryset = Submission.objects.all()
		resource_name = 'submission'
		excludes = ['require_order', 'require_all']
		always_return_data = True
		authentication = BasicAuthentication()
		authorization = Authorization()
		serializer = Serializer(formats=['json'])
	
	# This cannot be the best way of doing this, but deadlines are looming. 
	def post_list(self, request, **kwargs):

		self.method_check(request, allowed=['post'])
		data = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))

		# Get the slide node that the user is answering before creation of the submission -- this also needs further checks (e.g. can they even submit to this slide yet?)
		try:
			slide_node = Slide.objects.get(pk=data.get("slide_pk"))
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

		## TO-DO: Perform checks against the slide model to see if the user answered the question correctly (see above)
		node.save()

		return self.create_response(request, body)

	def patch_list(self, request, **kwargs):
		try:
			node = Submission.objects.select_related(depth=1).get(id=kwargs["pk"])
		except ObjectDoesNotExist:
			raise Http404("Cannot update non-existant submission")

