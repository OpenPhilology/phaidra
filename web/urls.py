from django.conf.urls import patterns, url

from web import views

urlpatterns = patterns('', 
	url(r'^module/', views.module, name='module'),
	url(r'^$', views.index, name='index'),
)
