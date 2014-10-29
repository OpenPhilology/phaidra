"""
Content resource for API endpoint
"""
from tastypie import fields
from tastypie.resources import ModelResource
from app.models import Content
from api.grammar import GrammarResource
from api.language import LanguageResource
from api.shallow_content import ShallowContentResource
import markdown

class ContentResource(ModelResource):
    source_lang = fields.ForeignKey(LanguageResource, 
                                    'source_lang', 
                                    null=True, 
                                    blank=True, 
                                    full=True)

    target_lang = fields.ForeignKey(LanguageResource, 
                                    'target_lang', 
                                    null=True, 
                                    blank=True, 
                                    full=True)

    grammar_ref = fields.ToOneField(GrammarResource, 
                                    'grammar_ref', 
                                    null=True, 
                                    blank=True)

    # This is to prevent infinite recursive includes
    related_content = fields.ManyToManyField(ShallowContentResource, 
                                    'related_content', 
                                    null=True, 
                                    blank=True, 
                                    full=True)

    class Meta:
        queryset = Content.objects.all()
        allowed_methods = ['get']
    
    def dehydrate_content(self, bundle):
        return markdown.markdown(bundle.data['content'], 
                                    ['markdown.extensions.tables', 'markdown.extensions.attr_list'])
