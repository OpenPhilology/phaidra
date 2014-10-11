from tastypie import fields
from tastypie.resources import ModelResource
from app.models import Content
import markdown

class ShallowContentResource(ModelResource):

	class Meta:
		queryset = Content.objects.all()
		allowed_methods = ['get']
	
	def dehydrate_content(self, bundle):
		return markdown.markdown(bundle.data['content'], ['markdown.extensions.tables'])
