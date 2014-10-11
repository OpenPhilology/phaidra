from tastypie import fields
from tastypie.resources import ModelResource
from app.models import Task

class TaskResource(ModelResource):
	
	class Meta:
		queryset = Task.objects.all()
		allowed_methods = ['get']
