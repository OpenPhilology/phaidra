from django.conf.urls import patterns, include, url

<<<<<<< HEAD
from api.api import UserResource
from api.api import SlideResource
from api.api import SubmissionResource

from api.api import DocumentResource
from api.api import SentenceResource
from api.api import WordResource
from api.api import LemmaResource

from api.api import SentenceShortResource
from api.api import TranslationResource

from api.api import VisualizationResource

user_resource = UserResource()
slide_resource = SlideResource()
submission_resource = SubmissionResource()

document_resource = DocumentResource()
sentence_resource = SentenceResource()
word_resource = WordResource()
lemma_resource = LemmaResource()

sentence_short_resource = SentenceShortResource()
translation_resource = TranslationResource()

visualization_resource = VisualizationResource()

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from tastypie.api import Api
from api.api import TextbookResource, UnitResource, LessonResource, SlideResource, UserResource 

v1_api = Api(api_name='v1')
v1_api.register(UserResource())
v1_api.register(TextbookResource())
v1_api.register(UnitResource())
v1_api.register(LessonResource())
v1_api.register(SlideResource())

urlpatterns = patterns('',

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

	url(r'api/', include(v1_api.urls)),

	url(r'^trees/', 'web.views.trees'),
	url(r'^lessons/', 'web.views.lessons'),
	url(r'^module/', 'web.views.module'),
	url(r'^viz/', 'web.views.viz'),
	url(r'^vocab/', 'web.views.vocab'),
	url(r'^profile/', 'web.views.profile'),
	url(r'^login/', 'web.views.login'),
	url(r'^$', 'web.views.index')
)
