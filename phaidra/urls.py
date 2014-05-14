from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from tastypie.api import Api
from api.api import TextbookResource, UnitResource, LessonResource, SlideResource, UserResource, SubmissionResource
from api.api import WordResource, SentenceResource, DocumentResource, LemmaResource
from api.api import VisualizationResource

v1_api = Api(api_name='v1')
v1_api.register(UserResource())
v1_api.register(TextbookResource())
v1_api.register(UnitResource())
v1_api.register(LessonResource())
v1_api.register(SlideResource())

v1_api.register(WordResource())
v1_api.register(SentenceResource())
v1_api.register(DocumentResource())
v1_api.register(LemmaResource())

v1_api.register(SubmissionResource())
v1_api.register(VisualizationResource())

urlpatterns = patterns('',

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

	url(r'api/', include(v1_api.urls)),

	url(r'^grammar/', 'web.views.grammar'),
	url(r'^trees/', 'web.views.trees'),
	url(r'^home/', 'web.views.home'),
	url(r'^lessons/', 'web.views.lessons'),
	url(r'^module/', 'web.views.module'),
	url(r'^reader/', 'web.views.reader'),
	url(r'^vocab/', 'web.views.vocab'),
	url(r'^profile/', 'web.views.profile'),
	url(r'^login/', 'web.views.login'),
	url(r'^$', 'web.views.index')
)
