"""
Grammar resource for API endpoint
"""
from tastypie import fields
from tastypie.resources import ModelResource
from app.models import Grammar
from api.task_context import TaskContextResource

class GrammarResource(ModelResource):
    content = fields.ForeignKey('api.content.ContentResource', 
                                'content', 
                                blank=True, 
                                null=True, 
                                use_in='detail', 
                                full=True)

    category = fields.ForeignKey('api.category.CategoryResource', 
                                'category', 
                                blank=True, 
                                null=True, 
                                full=True)

    task_sequence = fields.ForeignKey('api.task_sequence.TaskSequenceResource', 
                                'tasks', 
                                blank=True, 
                                full=True, 
                                null=True, 
                                use_in='detail')

    class Meta:
        queryset = Grammar.objects.all()
        allowed_methods = ['get']
