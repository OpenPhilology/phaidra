from tastypie.resources import ModelResource
from core.models.user import AppUser

class UserResource(ModelResource):
	class Meta:
		queryset = AppUser.objects.all()
		resource_name = 'user'
		excludes = ['password']
		allowed_methods = ['get']
