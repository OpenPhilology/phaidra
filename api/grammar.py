"""
Grammar resource for API endpoint
"""
from tastypie import fields
from tastypie.http import HttpResponse
from tastypie.resources import ModelResource
from app.models import Grammar, Content
from api.task_context import TaskContextResource
from api.content import ContentResource
import json

class GrammarResource(ModelResource):
    content = fields.ToManyField(ContentResource, 
                                'content_set', 
                                related_name='content',
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

    def build_title(self, memo, content):
        lang = content.source_lang.short_code
        memo[lang] = content 

        return memo

    def dehydrate(self, bundle):
        bundle.data['titles'] = reduce(self.build_title, Content.objects.filter(grammar_ref=bundle.obj), {})
        
        return bundle
