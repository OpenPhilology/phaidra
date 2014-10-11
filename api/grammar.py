from tastypie import fields
from tastypie.resources import ModelResource
from app.models import Grammar

class GrammarResource(ModelResource):
	content = fields.ForeignKey('api.content.ContentResource', 'content', blank=True, null=True, use_in='detail', full=True)
	category = fields.ForeignKey('api.category.CategoryResource', 'category', blank=True, null=True, full=True)

	class Meta:
		queryset = Grammar.objects.all()
		allowed_methods = ['get']
