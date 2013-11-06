from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication

from core.models.user import AppUser
from core.models.slide import Slide
from core.models.submission import Submission

class UserResource(ModelResource):
	class Meta:
		queryset = AppUser.objects.all()
		resource_name = 'auth/user'
		excludes = ['password']
		allowed_methods = ['get']
		authentication = BasicAuthentication()

class SlideResource(ModelResource):
	class Meta:
		queryset = Slide.objects.all()
		resource_name = 'slide'
		excludes = ['answers', 'require_order', 'require_all']

class SubmissionResource(ModelResource):
	class Meta:
		queryset = Submission.objects.all()
		resource_name = 'submission'
		excludes = ['require_order', 'require_all']
