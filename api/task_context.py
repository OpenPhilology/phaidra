from tastypie import fields
from tastypie.resources import ModelResource
from app.models import TaskContext

class TaskContextResource(ModelResource):
	task = fields.ToOneField('api.task.TaskResource', 'task', full=True, null=True, blank=True)

	class Meta:
		queryset = TaskContext.objects.all()
		allowed_methods = ['get']
