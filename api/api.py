from tastypie.resources import ModelResource
from neo4django.graph_auth.models import User
from core.models.slide import Slide

class UserResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'user'
		excludes = ['password']
		allowed_methods = ['get']

class SlideResource(ModelResource):
	class Meta:
		queryset = Slide.objects.all()
		resource_name = 'slide'
		excludes = ['answers', 'require_order', 'require_all']
