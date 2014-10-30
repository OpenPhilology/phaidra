"""
Language Resource for API endpoint.
Also used in GrammarResource, AppUserResource, ContentResource
"""
from tastypie import fields
from tastypie.resources import ModelResource
from app.models import Language

class LanguageResource(ModelResource):

    class Meta:
        queryset = Language.objects.all()
        allowed_methods = ['get']
        filtering = { 'short_code': ['exact'] } 
