from tastypie.resources import ModelResource
from core.models.user import AppUser
from core.models.slide import Slide
from core.models.submission import Submission

class UserResource(ModelResource):
	class Meta:
		queryset = AppUser.objects.all()
		resource_name = 'user'
		excludes = ['password']
		allowed_methods = ['get']

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
