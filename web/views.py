import os
import json
import hashlib

from django.http import HttpResponse
from django.template import RequestContext, loader

def index(request):
	template = loader.get_template('index.html')

	context = RequestContext(request, {
		'email_hash': hashlib.md5(request.user.email).hexdigest() if request.user.is_authenticated() else ''
	})

	return HttpResponse(template.render(context))

def lessons(request):
	template = loader.get_template('lessons.html')

	context = RequestContext(request, {
		'email_hash': hashlib.md5(request.user.email).hexdigest() if request.user.is_authenticated() else ''
	})

	return HttpResponse(template.render(context))

def trees(request):
	template = loader.get_template('trees.html')

	context = RequestContext(request, {
		'':''
	})

	return HttpResponse(template.render(context))

def login(request):
	template = loader.get_template('login.html')

	context = RequestContext(request, {
		'email_hash': hashlib.md5(request.user.email).hexdigest() if request.user.is_authenticated() else ''
	})

	return HttpResponse(template.render(context))

def viz(request):
	template = loader.get_template('viz.html')
	context = RequestContext(request, {
		'email_hash': hashlib.md5(request.user.email).hexdigest() if request.user.is_authenticated() else ''
	})

	return HttpResponse(template.render(context))

def profile(request):
	template = loader.get_template('profile.html')
	context = RequestContext(request, {
		'email_hash': hashlib.md5(request.user.email).hexdigest() if request.user.is_authenticated() else ''
	})

	return HttpResponse(template.render(context))

def vocab(request):
	template = loader.get_template('vocab.html')
	context = RequestContext(request, {
		'email_hash': hashlib.md5(request.user.email).hexdigest() if request.user.is_authenticated() else ''
	})

	return HttpResponse(template.render(context))

def module(request):
	template = loader.get_template('module.html')
	context = RequestContext(request, {
		'email_hash': hashlib.md5(request.user.email).hexdigest() if request.user.is_authenticated() else ''
	})

	return HttpResponse(template.render(context))
