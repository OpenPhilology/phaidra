"""
Grammar resource for API endpoint
"""
from tastypie import fields
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
from app.models import Grammar
from api.task_context import TaskContextResource

class GrammarResource(ModelResource):
    content = fields.ToManyField('api.content.ContentResource', 
                                'content_set', 
                                related_name='content',
                                blank=True, 
                                null=True, 
                                use_in='detail', 
                                full=True)

    #hr_title = fields.CharField(attribute='content__title')

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
        filtering = { 'content': ALL_WITH_RELATIONS }
