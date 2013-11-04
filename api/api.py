from tastypie.resources import ModelResource
from neo4django.graph_auth.models import User

class UserResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'user'
