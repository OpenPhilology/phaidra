from django.conf.urls import patterns, include, url
#from web import views
#from rest_framework import routers

from api.api import UserResource
from api.api import SlideResource
from api.api import SubmissionResource

from api.api import DocumentResource
from api.api import SentenceResource
from api.api import WordResource
from api.api import LemmaResource
from api.api import LemmaWordResource

user_resource = UserResource()
slide_resource = SlideResource()
submission_resource = SubmissionResource()

document_resource = DocumentResource()
sentence_resource = SentenceResource()
word_resource = WordResource()
lemma_word_resource = LemmaWordResource()
lemma_resource = LemmaResource()

#router = routers.DefaultRouter()
#router.register(r'api/users', views.UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

	url(r'^module/', 'web.views.module'),
	url(r'^viz/', 'web.views.viz'),
	url(r'^vocab/', 'web.views.vocab'),
	url(r'^profile/', 'web.views.profile'),
	url(r'^login/', 'web.views.login'),
	url(r'^$', 'web.views.index'),
	url(r'^api/', include(user_resource.urls)),
	url(r'^api/', include(slide_resource.urls)),
	url(r'^api/', include(submission_resource.urls)),

	url(r'^api/', include(document_resource.urls)),
	url(r'^api/', include(sentence_resource.urls)),
	url(r'^api/', include(word_resource.urls)),
    url(r'^api/', include(lemma_word_resource.urls)),
    url(r'^api/', include(lemma_resource.urls)),

	#url(r'^', include(router.urls)),
	#url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
