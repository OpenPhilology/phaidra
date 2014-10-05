from tastypie.resources import ModelResource
from app.models import Grammar

class GrammarResource(ModelResource):
	class Meta:
		queryset = Grammar.objects.all()
		allowed_methods = ['get']
