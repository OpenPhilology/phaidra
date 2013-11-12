from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import Http404

from core.models.user import AppUser
from core.models.slide import Slide
from core.models.submission import Submission

from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.utils import trailing_slash
from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized

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
		authorization = UserObjectsOnlyAuthorization()
	
	#
	#  Everything below this line, untested! Todo:
	# 		- Route different types of requests (GET, POST/PUT, PATCH) to do appropriate actions
	#		- Make this actually work...somehow.
	#

	def prepend_urls(self):
		return [
			#url(r"^submission/", self.wrap_view('post_or_put_submission'), name="api_post_or_put_submission"),
			url(r"^submission/(?P<pk>[0-9]*)/", self.wrap_view('patch_submission'), name="api_patch_submission")
		]

	def post_or_put_submission(self, request, **kwargs):

		self.method_check(request, allowed=['post'])
		data = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))

		try:
			node = Submission.objects.create(
				value = data.get("value"),
				started = data.get("started"),
				finished = data.get("finished")
			)
		except IntegrityError as e:
			return self.create_response(request, {
				'success': False,
				'error': e
			})

		# Get the slide node that the user is answering
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
			# Is it possible this could occur if the user passes authorization checks?
			return self.create_response(request, {
				'success': False,
				'error': e
			})

		# Form the connections from the new Submission node to the existing slide and user nodes
		node.add(slide_node)
		node.add(user_node)

		# Modify the request and serve it back to the user along with a success message!
		body = json.loads(request.body) if type(request.body) is str else request.body
		## TO-DO: Perform checks against the slide model to see if the user answered the question correctly

		node.save()
		return self.create_response(request, body)

	def patch_submission(self, request, **kwargs):
		try:
			node = Submission.objects.select_related(depth=1).get(id=kwargs["pk"])
		except ObjectDoesNotExist:
			raise Http404("Cannot update non-existant submission")
