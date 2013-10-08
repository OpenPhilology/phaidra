from django.conf.urls import patterns, include, url
from web import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('web.views',

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),


	url(r'^module/', 'module'),
	url(r'^viz/', 'viz'),
	url(r'^vocab/', 'vocab'),
	url(r'^profile/', 'profile'),
	url(r'^$', 'index'),
)
