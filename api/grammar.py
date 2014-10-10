from tastypie import fields
from tastypie.resources import ModelResource
from app.models import Grammar

class GrammarResource(ModelResource):
	content = fields.ForeignKey('api.content.ContentResource', 'content', blank=True, null=True, use_in='detail', full=True)
	related_content = fields.ToManyField('api.content.ContentResource', 'relates_to', null=True, blank=True, full=True, use_in='detail')

	class Meta:
		queryset = Grammar.objects.all()
		allowed_methods = ['get']
