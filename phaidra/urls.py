from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.shortcuts import redirect

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from tastypie.api import Api

from api.user import UserResource
from api.create_user import CreateUserResource
from api.contribute import UserSentenceResource, UserDocumentResource
from api.submission import SubmissionResource
from api.visualization import VisualizationResource
from api.document import DocumentResource
from api.sentence import SentenceResource
from api.word import WordResource
from api.lemma import LemmaResource

from api.grammar import GrammarResource
from api.content import ContentResource
from api.language import LanguageResource

v1_api = Api(api_name='v1')
v1_api.register(UserResource())
v1_api.register(CreateUserResource())
v1_api.register(GrammarResource())
v1_api.register(ContentResource())
v1_api.register(LanguageResource())

v1_api.register(WordResource())
v1_api.register(SentenceResource())
v1_api.register(DocumentResource())
v1_api.register(LemmaResource())

v1_api.register(SubmissionResource())
v1_api.register(VisualizationResource())

v1_api.register(UserDocumentResource())
v1_api.register(UserSentenceResource())

js_info_dict = {
    'packages': ('phaidra',)
}

urlpatterns = patterns('',

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # API Urls
    url(r'api/', include(v1_api.urls)),

    # JS Localization
    url(r'^templates/(?P<path>\w+)', 'web.views.static'),
    url(r'^jsi8n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    url(r'^i18n/', include('django.conf.urls.i18n')),

    # Logout
    url(r'^logout/', 'django.contrib.auth.views.logout', {'next_page': '/'}),
)

urlpatterns += i18n_patterns('', 

    # Website URLS
    url(r'^lessons/', 'web.views.lessons'),
    url(r'^create/', 'web.views.create'),
    url(r'^module/', 'web.views.module'),
    url(r'^reader/', 'web.views.reader'),
    url(r'^profile/', 'web.views.profile'),
    url(r'^login/', 'web.views.login'),
    url(r'^aboutus/', 'web.views.aboutus'),
    url(r'^$', 'web.views.index')
)

