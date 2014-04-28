from __future__ import unicode_literals
# coding: utf8
from phaidra import settings
from phaidra.urls import v1_api

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phaidra.settings")
from django.conf import settings
from django.contrib.auth.models import User
from app.models import Textbook, Unit, Lesson, Slide

from tastypie import fields
from tastypie.resources import Resource, ModelResource

from neo4jrestclient.client import GraphDatabase
#from neo4jrestclient import client

from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.authentication import SessionAuthentication
from tastypie.authorization import Authorization, ReadOnlyAuthorization
#from tastypie.exceptions import Unauthorized
#from tastypie.utils import trailing_slash
from tastypie.http import HttpUnauthorized, HttpForbidden, HttpBadRequest

import json
import random
from random import shuffle

import time

#db = GraphDatabase('/var/lib/neo4j/data/graph.db/')

class TextbookResource(ModelResource):
	class Meta:
		queryset = Textbook.objects.all()
		resource_name = 'textbook'
		allowed_methods = ['get']

class UnitResource(ModelResource):
	class Meta:
		queryset = Unit.objects.all()
		resource_name = 'unit'
		allowed_methods = ['get']

class LessonResource(ModelResource):
	class Meta:
		queryset = Lesson.objects.all()
		resource_name = 'lesson'
		allowed_methods = ['get']

class SlideResource(ModelResource):
	class Meta:
		queryset = Slide.objects.all()
		resource_name = 'slide'
		allowed_methods = ['get']

class UserResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'user'
		fields = ['username', 'first_name', 'last_name', 'last_login']
		

		
class DataObject(object):
	
    def __init__(self, id=None, cts=None):
    	
    	self.__dict__['_data'] = {}
    	
    	if not hasattr(id, 'id') and id is not None:
    		
    		gdb = GraphDatabase("http://localhost:7474/db/data/")
        	word = gdb.nodes.get("http://localhost:7474/db/data/node/" + id)
        	self.__dict__['_data'] = word.properties
         	self.__dict__['_data']['id'] = id       	

    def __getattr__(self, name):
        return self._data.get(name, None)

    def __setattr__(self, name, value):
        self.__dict__['_data'][name] = value

    def to_dict(self):
        return self._data


class WordResource(Resource):
	
	CTS = fields.CharField(attribute='CTS')
	value = fields.CharField(attribute='value')
	form = fields.CharField(attribute='form', null = True, blank = True)
	lemma = fields.CharField(attribute='lemma', null = True, blank = True)
	
	sentence = fields.CharField(attribute='sentence', null = True, blank = True)
	
	length = fields.IntegerField(attribute='length', null = True, blank = True)
	tbwid = fields.IntegerField(attribute='tbwid')
	head = fields.IntegerField(attribute='head')
	cid = fields.IntegerField(attribute='cid', null = True, blank = True)
	
	pos = fields.CharField(attribute='pos', null = True, blank = True)
	person = fields.CharField(attribute='person', null = True, blank = True)
	number = fields.CharField(attribute='number', null = True, blank = True)
	tense = fields.CharField(attribute='tense', null = True, blank = True)
	mood = fields.CharField(attribute='mood', null = True, blank = True)
	voice = fields.CharField(attribute='voice', null = True, blank = True)
	gender = fields.CharField(attribute='gender', null = True, blank = True)
	case = fields.CharField(attribute='case', null = True, blank = True)
	degree = fields.CharField(attribute='degree', null = True, blank = True)
	
	relation = fields.CharField(attribute='relation', null = True, blank = True)	
	
	dialect = fields.CharField(attribute='dialect', null = True, blank = True)
	posClass = fields.CharField(attribute='posClass', null = True, blank = True)
	posAdd = fields.CharField(attribute='posAdd', null = True, blank = True)
	isIndecl = fields.CharField(attribute='isIndecl', null = True, blank = True)
	
	
	class Meta:
	
		resource_name = 'word'
		object_class = DataObject
		authorization = ReadOnlyAuthorization()
	
	
	def detail_uri_kwargs(self, bundle_or_obj):
		
		kwargs = {}
		
		if isinstance(bundle_or_obj, Bundle):
			kwargs['pk'] = bundle_or_obj.obj.id
			
		else:
			kwargs['pk'] = bundle_or_obj.id
			
		return kwargs
	
	#/api/word/?randomized=&format=json&lemma=κρατέω
	def get_object_list(self, request):
		
		gdb = GraphDatabase("http://localhost:7474/db/data/")	
		attrlist = ['CTS', 'length', 'case', 'dialect', 'head', 'form', 'posClass', 'cid', 'gender', 'tbwid', 'pos', 'value', 'degree', 'number','lemma', 'relation', 'isIndecl', 'ref', 'posAdd', 'mood', 'tense', 'voice', 'person']
		words = []
		
		query_params = {}
		for obj in request.GET.keys():
			if obj in attrlist and request.GET.get(obj) is not None:
				query_params[obj] = request.GET.get(obj)
			elif obj.split('__')[0] in attrlist and request.GET.get(obj) is not None:
				query_params[obj] = request.GET.get(obj)
		
		# implement filtering
		if len(query_params) > 0:
			
			# generate query
			q = """START s=node(*) MATCH (s)-[:words]->(w) WHERE """
			
			# filter word on parameters
			for key in query_params:
				if len(key.split('__')) > 1:
					if key.split('__')[1] == 'contains':
						q = q + """HAS (w.""" +key.split('__')[0]+ """) AND w.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """.*' AND """
					elif key.split('__')[1] == 'startswith':
						q = q + """HAS (w.""" +key.split('__')[0]+ """) AND w.""" +key.split('__')[0]+ """=~'""" +query_params[key]+ """.*' AND """
					elif key.split('__')[1] == 'endswith':
						q = q + """HAS (w.""" +key.split('__')[0]+ """) AND w.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """' AND """
				else:
					q = q + """HAS (w.""" +key+ """) AND w.""" +key+ """='""" +query_params[key]+ """' AND """
			q = q[:len(q)-4]
			q = q + """RETURN w, s"""
			
			table = gdb.query(q)
		
		# default querying	
		else:	
			table = gdb.query("""START s=node(*) MATCH (s)-[:words]->(w) WHERE HAS (w.CTS) RETURN w, s""")
			
		# create the objects which was queried for and set all necessary attributes
		for t in table:
			word = t[0]
			sentence = t[1]
			new_obj = DataObject(id=None, cts=None)
			new_obj.__dict__['_data'] = word['data']
			url = word['self'].split('/')
			urlSent = sentence['self'].split('/')
			new_obj.__dict__['_data']['id'] = url[len(url)-1]
			new_obj.__dict__['_data']['sentence'] =  '/api/' +  v1_api.api_name + '/sentence/' + urlSent[len(urlSent)-1] +'/'
			words.append(new_obj)
				
		return words
	
	
	def obj_get_list(self, bundle, **kwargs):
		
		return self.get_object_list(bundle.request)
	
	def obj_get(self, bundle, **kwargs):
		
		return DataObject(id=kwargs['pk'])
	
	
	class node(object):
		
		def __init__(self, value):
			self.value = value
			self.children = []
			
		def add_child(self, obj):
			self.children.append(obj)
			
			
	"""
	Function for shortening a sentence
	"""	
	def shorten(self, wordArray, params = None):
		
		words = wordArray		
		# interrupt as soon as possible if there is no according syntactical information available
		try:
			words[0]['head']
		except KeyError as k:
			return None
			
		# save words within a map for faster lookup			
		nodes = dict((word['tbwid'], self.node(word)) for word in words)
		# build a "tree"
		verbs = []
		for w in words:
			if w['head'] is not 0:
	   			nodes[w['head']].add_child(nodes[w['tbwid']])
	   		if w['relation'] == "PRED" or w['relation'] == "PRED_CO":
	   			verbs.append(w)
														
		# start here 
		for verb in verbs:					
			# get the verb
			if verb['relation'] == "PRED" or verb['relation'] == "PRED_CO":						
				u, i = [], []
				aim_words = []
				# group the words and make sure, save the selected words
				for word in nodes[verb['tbwid']].children:
											
					if word.value['relation'] == "COORD":
						u.append(word.value['tbwid'])
						#aim_words.append(word)
						for w in nodes[word.value['tbwid']].children:
							if (w.value['relation'] == "OBJ_CO" or w.value['relation'] == "ADV_CO") and w.value['pos'] != "participle" and w.value['pos'] != "verb":
								i.append(w.value['tbwid'])
								aim_words.append(w.value)
					
					elif word.value['relation'] == "AuxP":
						aim_words.append(word.value)
						for w in nodes[word.value['tbwid']].children:
							if w.value['relation'] != "AuxC" and w.value['pos'] != "participle":
								aim_words.append(w.value)
					
								for w2 in nodes[w.value['tbwid']].children:
									if w2.value['relation'] == "ATR" and w2.value['pos'] != "verb":
										aim_words.append(w2.value)
										
										
					elif word.value['relation'] != "AuxC" and word.value['relation'] != "COORD" and word.value['pos'] != "participle":
						aim_words.append(word.value)
						for w in nodes[word.value['tbwid']].children:
							if w.value['relation'] == "ATR" and w.value['pos'] != "verb":
								aim_words.append(w.value)
					
				# refinement of u
				for id in u:
					for id2 in i:
						w = nodes[id2].value
						if w['head'] is id:
							aim_words.append(w)   
							
				aim_words.append(verb)
					
				# check if not verbs only are returned
				if len(aim_words) > 1:
					# consider params
					if len(params) > 0:
						# check if aim_words and parameter filtered intersect 
						cand = False
						for w in aim_words:
							for key in params:
								if w[key] == params[key]:
									cand = True
								else:
									cand = False
									continue
							
							if cand:										
								# set and order words
								return sorted(aim_words, key=lambda x: x['tbwid'], reverse=False)	
						
						return None		
					else:		
						# set and order words
						return sorted(aim_words, key=lambda x: x['tbwid'], reverse=False)
					
					
					# set and order words
					return sorted(aim_words, key=lambda x: x['tbwid'], reverse=False)
									
		return None

 


   
