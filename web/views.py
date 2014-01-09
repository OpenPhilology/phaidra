import os
import json

from django.http import HttpResponse
from django.template import RequestContext, loader

def index(request):
	template = loader.get_template('index.html')

	"""
	This placeholder data will be loaded from .json files,
	and eventually generated dynamically.
	"""

	context = RequestContext(request, {
		'name' : 'Learn the Greek Alphabet',
		'content' : '...'
	})

	return HttpResponse(template.render(context))

def login(request):
	template = loader.get_template('login.html')

	context = RequestContext(request, {
		'name' : 'Learn the Greek Alphabet',
		'content' : '...'
	})

	return HttpResponse(template.render(context))

def viz(request):
	template = loader.get_template('viz.html')
	context = RequestContext(request, {
		'title' : 'Learn the Greek Alphabet',
		'content' : ''
	})

	return HttpResponse(template.render(context))

def profile(request):
	template = loader.get_template('profile.html')
	context = RequestContext(request, {
		'title' : 'Learn the Greek Alphabet',
		'content' : ''
	})

	return HttpResponse(template.render(context))

def vocab(request):
	template = loader.get_template('vocab.html')
	context = RequestContext(request, {
		'title' : 'Learn the Greek Alphabet',
		'content' : ''
	})

	return HttpResponse(template.render(context))

def module(request):
	template = loader.get_template('module.html')
	context = RequestContext(request, {
		'title' : 'Learn the Greek Alphabet',
		'content' : ''
	})

	return HttpResponse(template.render(context))
