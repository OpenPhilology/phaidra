from tastypie.resources import ModelResource
from app.models import Content
import markdown

class ContentResource(ModelResource):
	class Meta:
		queryset = Content.objects.all()
		allowed_methods = ['get']
	
	def dehydrate_content(self, bundle):
		return markdown.markdown(bundle.data['content'], ['markdown.extensions.tables'])
