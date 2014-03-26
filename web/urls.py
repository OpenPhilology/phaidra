from django.conf.urls import patterns, url

from web import views

urlpatterns = patterns('', 
	url(r'^trees/', views.trees, name='trees'),
	url(r'^module/', views.module, name='module'),
	url(r'^viz/', views.viz, name='viz'),
	url(r'^vocab/', views.vocab, name='vocab'),
	url(r'^profile/', views.profile, name='profile'),
	url(r'^login/', views.login, name='login'),
	url(r'^$', views.index, name='index'),
)
