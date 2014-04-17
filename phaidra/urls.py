from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from api.api import TextbookResource
textbook_resource = TextbookResource()

urlpatterns = patterns('',

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

	url(r'api/', include(textbook_resource.urls)),

	url(r'^trees/', 'web.views.trees'),
	url(r'^module/', 'web.views.module'),
	url(r'^viz/', 'web.views.viz'),
	url(r'^vocab/', 'web.views.vocab'),
	url(r'^profile/', 'web.views.profile'),
	url(r'^login/', 'web.views.login'),
	url(r'^$', 'web.views.index'),

)
