"""
Task Sequence Resource, used in Grammar Resource
"""
from tastypie import fields
from tastypie.resources import ModelResource
from app.models import TaskSequence
from api.task_context import TaskContextResource

class TaskSequenceResource(ModelResource):
    tasks = fields.ManyToManyField(TaskContextResource, 
                                    attribute=lambda bundle: 
                                    bundle.obj.tasks.through.objects.filter(task_sequence=bundle.obj) 
                                    or bundle.obj.tasks, 
                                    full=True)

    class Meta:
        queryset = TaskSequence.objects.all()
        allowed_methods = ['get']
