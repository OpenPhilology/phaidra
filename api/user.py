from __future__ import unicode_literals
# coding: utf-8
from phaidra.settings import CTS_LANG
from phaidra.settings import GRAPH_DATABASE_REST_URL, API_PATH

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phaidra.settings")
from django.conf.urls import url
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import authenticate

from neo4jrestclient.client import GraphDatabase, Node, Relationship

from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.authentication import SessionAuthentication, BasicAuthentication, Authentication
from tastypie.authorization import Authorization
from tastypie.utils import trailing_slash
from tastypie.http import HttpUnauthorized, HttpForbidden, HttpBadRequest
from tastypie.exceptions import NotFound, BadRequest, Unauthorized
from tastypie.resources import Resource, ModelResource
from tastypie.serializers import Serializer

from datetime import datetime

import dateutil.parser

import json
import operator
import time
import urlparse

from api import DataObject

class UserSentenceResource(Resource):
    
    CTS = fields.CharField(attribute='CTS', null = True, blank = True)
    sentence = fields.CharField(attribute='sentence', null = True, blank = True)    
    length = fields.IntegerField(attribute='length', null = True, blank = True)
    document_resource_uri = fields.CharField(attribute='document_resource_uri', null = True, blank = True)
    words = fields.ListField(attribute='words', null = True, blank = True)
    translations = fields.DictField(attribute='translations', null = True, blank = True)
    user = fields.CharField(attribute='user', null = True, blank = True)
    
    class Meta:
        
        resource_name = 'user_sentence'
        object_class = DataObject
        authorization = Authorization() 
        authentication = BasicAuthentication()   
    
    def detail_uri_kwargs(self, bundle_or_obj):
        
        kwargs = {}
        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.id    
        else:
            kwargs['pk'] = bundle_or_obj.id    
        return kwargs


    def get_object_list(self, request):
        
        gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)    
        attrlist = ['CTS', 'length', 'sentence']
        sentences = []
        
        query_params = {}
        for obj in request.GET.keys():
            if obj in attrlist and request.GET.get(obj) is not None:
                query_params[obj] = request.GET.get(obj)
            elif obj.split('__')[0] in attrlist and request.GET.get(obj) is not None:
                query_params[obj] = request.GET.get(obj)
        
        # implement filtering
        if len(query_params) > 0:
            
            # generate query
            q = """MATCH (u:`User`)-[:owns]->(d:UserDocument)-[:sentences]->(s:UserSentence) WHERE """
            
            # filter word on parameters
            for key in query_params:
                if len(key.split('__')) > 1:
                    if key.split('__')[1] == 'contains':
                        q = q + """HAS (s.""" +key.split('__')[0]+ """) AND s.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """.*' AND """
                    elif key.split('__')[1] == 'startswith':
                        q = q + """HAS (s.""" +key.split('__')[0]+ """) AND s.""" +key.split('__')[0]+ """=~'""" +query_params[key]+ """.*' AND """
                    elif key.split('__')[1] == 'endswith':
                        q = q + """HAS (s.""" +key.split('__')[0]+ """) AND s.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """' AND """
                else:
                    q = q + """HAS (s.""" +key+ """) AND s.""" +key+ """='""" +query_params[key]+ """' AND """
            # is user set if params not empty?
         	if request.GET.get('user'):
         		q = q + """ u.username='""" + request.GET.get('user') + """' RETURN s, d, u ORDER BY ID(s)"""         		
         	else:
         		q = q[:len(q)-4]
         		q = q + """RETURN s, d, u ORDER BY ID(s)"""
            
        	table = gdb.query(q)
        
        # default querying    
        else:    
            # is user set if params are empty?
        	if request.GET.get('user'):
         		table = gdb.query("""MATCH (u:`User`)-[:owns]->(d:`UserDocument`)-[:sentences]->(s:UserSentence) WHERE u.username='""" + request.GET.get('user') + """' RETURN DISTINCT s, d, u ORDER BY ID(d)""")
         	else:
         		table = gdb.query("""MATCH (u:`User`)-[:owns]->(d:UserDocument)-[:sentences]->(s:UserSentence) RETURN s, d, u ORDER BY ID(s)""")
            
            
        # create the objects which was queried for and set all necessary attributes
        for t in table:
            sentence = t[0]
            document = t[1]   
            user = t[2]     
            url = sentence['self'].split('/')
            urlDoc = document['self'].split('/')        
                
            new_obj = DataObject(url[len(url)-1])
            new_obj.__dict__['_data'] = sentence['data']        
            new_obj.__dict__['_data']['id'] = url[len(url)-1]
            new_obj.__dict__['_data']['document_resource_uri'] = API_PATH + 'user_document/' + urlDoc[len(urlDoc)-1] +'/'
            new_obj.__dict__['_data']['user'] = user['data']['username']
            sentences.append(new_obj)
                
        return sentences
    
    def obj_get_list(self, bundle, **kwargs):
        
        return self.get_object_list(bundle.request)
    
    def obj_get(self, bundle, **kwargs):
        
        # query parameters (optional) for short sentence approach
        attrlist = ['CTS', 'length', 'case', 'dialect', 'head', 'form', 'posClass', 'cid', 'gender', 'tbwid', 'pos', 'value', 'degree', 'number','lemma', 'relation', 'isIndecl', 'ref', 'posAdd', 'mood', 'tense', 'voice', 'person']
        query_params = {}
        for obj in bundle.request.GET.keys():
            if obj in attrlist and bundle.request.GET.get(obj) is not None:
                query_params[obj] = bundle.request.GET.get(obj)
            elif obj.split('__')[0] in attrlist and bundle.request.GET.get(obj) is not None:
                query_params[obj] = bundle.request.GET.get(obj)
        
        gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)
        sentence = gdb.nodes.get(GRAPH_DATABASE_REST_URL + "node/" + kwargs['pk'] + '/')
        documentNode = sentence.relationships.incoming(types=["sentences"])[0].start
        # get the sentence parameters            
        new_obj = DataObject(kwargs['pk'])
        new_obj.__dict__['_data'] = sentence.properties
        new_obj.__dict__['_data']['id'] = kwargs['pk']
        new_obj.__dict__['_data']['document_resource_uri'] = API_PATH + 'user_document/' + str(sentence.relationships.incoming(types=["sentences"])[0].start.id) + '/'
        new_obj.__dict__['_data']['user'] = str(documentNode.relationships.incoming(types=["owns"])[0].start.properties['username'])
        
        # get a dictionary of related translation of this sentence # shall this be more strict (only user)
        relatedSentences = gdb.query("""MATCH (s:`UserSentence`)-[:words]->(w:`Word`)-[:translation]->(t:`Word`)<-[:words]-(s1:`Sentence`) WHERE HAS (s.CTS) AND s.CTS='""" + sentence.properties['CTS'] + """' RETURN DISTINCT s1 ORDER BY ID(s1)""")
        
        new_obj.__dict__['_data']['translations']={}
        for rs in relatedSentences:
            sent = rs[0]
            url = sent['self'].split('/')
            for lang in CTS_LANG:
                if sent['data']['CTS'].find(lang) != -1:
                    new_obj.__dict__['_data']['translations'][lang] = API_PATH + 'sentence/' + url[len(url)-1] +'/'        
        
        # get the words and related information    
        words = gdb.query("""MATCH (d:`UserSentence`)-[:words]->(w:`Word`) WHERE d.CTS='""" +sentence.properties['CTS']+ """' RETURN DISTINCT w ORDER BY ID(w)""")
        wordArray = []
        for w in words:
            word = w[0]
            url = word['self'].split('/')
            word['data']['resource_uri'] = API_PATH + 'word/' + url[len(url)-1] + '/'
            wordNode = gdb.nodes.get(GRAPH_DATABASE_REST_URL + "node/" + url[len(url)-1] + '/')
            
            # get the lemma # not on user document translations   
            #lemmaRels = wordNode.relationships.incoming(types=["values"])
            #if len(lemmaRels) > 0:
            #    word['data']['lemma_resource_uri'] = API_PATH + 'lemma/' + str(lemmaRels[0].start.id) + '/'
            
            # get the full translation
            if bundle.request.GET.get('full'):            
                translations = gdb.query("""MATCH (d:`Word`)-[:translation]->(w:`Word`) WHERE d.CTS='""" +wordNode.properties['CTS']+ """' RETURN DISTINCT w ORDER BY ID(w)""")
                translationArray = []
                for t in translations:
                    trans = t[0]
                    transurl = trans['self'].split('/')
                    trans['data']['resource_uri'] = API_PATH + 'word/' + transurl[len(transurl)-1] + '/'
                    translationArray.append(trans['data'])
                word['data']['translations'] = translationArray
                
            wordArray.append(word['data'])
            
        # if short=True return only words of the short sentence
        if bundle.request.GET.get('short'):
            wordArray =  self.shorten(wordArray, query_params)
            if wordArray is None:
                #return None
                raise BadRequest("Sentence doesn't hit your query.")
        
        
        new_obj.__dict__['_data']['words'] = wordArray

        return new_obj


    # means csrftoken and sessionid  is required, if resource on session auth?!    
    def post_list(self, request, **kwargs):
        """
        Create a new sentence object, and the word objects containing the translations, build the relations; return the json data.
        """
        gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)
        
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        
        if not request.user or not request.user.is_authenticated():
            return self.create_response(request, { 'success': False, 'error_message': 'You are not authenticated, %s.' % request.user })

        data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
        if data.get("document_resource_uri") is None :
            raise ValidationError('document_resource_uri required.')
        documentResourceUriArray = data.get("document_resource_uri").split('/')
        documentId = documentResourceUriArray[len(documentResourceUriArray)-2]
        
        # get the user and document via neo look-up or create a new one
        if request.user.username is not None:
            documentTable = gdb.query("""MATCH (u:`User`)-[:owns]->(d:`UserDocument`) WHERE HAS (u.username) AND ID(d)=""" + documentId +""" AND u.username='""" + request.user.username + """' RETURN u,d""")        
            # test for user node
            try:
                documentTable.elements[0][0]
            except ValidationError:
                return self.error_response(request, {'error': 'User does not exist.'}, response_class=HttpBadRequest)
            
            try:
                documentTable.elements[0][1]
            except ValidationError:
                return self.error_response(request, {'error': 'Document does not exist.'}, response_class=HttpBadRequest)
            
            document = gdb.nodes.get(documentTable[0][1]['self'])
                                      
            # create sentence object        
            sentence = gdb.nodes.create(CTS = data.get("CTS"), length = len(data.get("words")))
            sentence.labels.add("UserSentence")
                
            # loop to create words
            sentencestring = ''
            for w in data.get("words"):
                sentencestring = sentencestring + "" + w["value"] + " "
                word = gdb.nodes.create( CTS = w["CTS"], lang = w["lang"], length = len(w["value"]), tbwid = w["tbwid"], value = w["value"])
                word.labels.add("Word")
                # loop to create links to translations
                for cts in w["translations"]:
                    translation = gdb.query("""MATCH (w:`Word`) WHERE HAS (w.CTS) AND w.CTS='""" + cts +"""' RETURN w""")
                    transNode = gdb.nodes.get(translation[0][0]['self'])
                    transNode.translation(word)
                    word.translation(transNode)
                    
                sentence.words(word)
                    
            # sentence as string
            sentence['sentence'] = sentencestring
            # documetn sentence relation
            document.sentences(sentence)
            
            # maybe here some extra resource _uro_informatin to return    
            #data['resource_uri'] = '/api/v1/document_user/' + str(document.id) + '/'
                
            if sentence is None :            
                raise ValidationError('Document node could not be created.')
            
            # save sentence to document
            #userNode.owns(document)
                  
            return self.create_response(request, data)
        
        else:
            return self.error_response(request, {'error': 'User is required.' }, response_class=HttpBadRequest)



class UserDocumentResource(Resource):
    
    CTS = fields.CharField(attribute='CTS')
    name = fields.CharField(attribute='name', null = True, blank = True)    
    lang = fields.CharField(attribute='lang', null = True, blank = True)
    author = fields.CharField(attribute='author', null = True, blank = True)
    sentences = fields.ListField(attribute='sentences', null = True, blank = True)
    translations = fields.DictField(attribute='translations', null = True, blank = True)
    user = fields.CharField(attribute='user', null = True, blank = True)
        
    class Meta:
        
        resource_name = 'user_document'
        object_class = DataObject
        allowed_methods = ['get', 'post']
        authorization = Authorization()
        authentication = BasicAuthentication()
    
    def detail_uri_kwargs(self, bundle_or_obj):
        
        kwargs = {}    
        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.id    
        else:
            kwargs['pk'] = bundle_or_obj.id        
        return kwargs
    
    def get_object_list(self, request):
        
        gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)    
        attrlist = ['CTS', 'name', 'name_eng', 'lang', 'author']
        documents = []
        
        query_params = {}
        for obj in request.GET.keys():
            if obj in attrlist and request.GET.get(obj) is not None:
                query_params[obj] = request.GET.get(obj)
            elif obj.split('__')[0] in attrlist and request.GET.get(obj) is not None:
                query_params[obj] = request.GET.get(obj)
        
        # implement filtering
        if len(query_params) > 0:
            
            # generate query
            q = """MATCH (u:`User`)-[:owns]->(d:`UserDocument`) WHERE """
            
            # filter word on parameters
            for key in query_params:
                if len(key.split('__')) > 1:
                    if key.split('__')[1] == 'contains':
                        q = q + """HAS (d.""" +key.split('__')[0]+ """) AND d.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """.*' AND """
                    elif key.split('__')[1] == 'startswith':
                        q = q + """HAS (d.""" +key.split('__')[0]+ """) AND d.""" +key.split('__')[0]+ """=~'""" +query_params[key]+ """.*' AND """
                    elif key.split('__')[1] == 'endswith':
                        q = q + """HAS (d.""" +key.split('__')[0]+ """) AND d.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """' AND """
                else:
                    q = q + """HAS (d.""" +key+ """) AND d.""" +key+ """='""" +query_params[key]+ """' AND """     	
         	# is user set if params not empty?
         	if request.GET.get('user'):
         		q = q + """ u.username='""" + request.GET.get('user') + """' RETURN d, u ORDER BY ID(d)"""         		
         	else:
         		q = q[:len(q)-4]
         		q = q + """RETURN d, u ORDER BY ID(d)"""
            
        	table = gdb.query(q)
        	      
        # default querying    
        else: 
        	# is user set if params are empty?
        	if request.GET.get('user'):
         		table = gdb.query("""MATCH (u:`User`)-[:owns]->(d:`UserDocument`) WHERE u.username='""" + request.GET.get('user') + """' RETURN DISTINCT d, u ORDER BY ID(d)""")
         	else:
         		table = gdb.query("""MATCH (u:`User`)-[:owns]->(d:`UserDocument`) RETURN DISTINCT d, u ORDER BY ID(d)""")
        # create the objects which was queried for and set all necessary attributes
        for t in table:
            document = t[0] 
            user = t[1]       
            urlDoc = document['self'].split('/')        
                
            new_obj = DataObject(urlDoc[len(urlDoc)-1])
            new_obj.__dict__['_data'] = document['data']        
            new_obj.__dict__['_data']['id'] = urlDoc[len(urlDoc)-1]
            new_obj.__dict__['_data']['user'] = user['data']['username']
            
            sentences = gdb.query("""MATCH (d:`UserDocument`)-[:sentences]->(s:`UserSentence`) WHERE d.CTS='""" +document['data']['CTS']+ """' RETURN DISTINCT s ORDER BY ID(s)""")
            sentenceArray = []
            for s in sentences:
                
                sent = s[0]
                url = sent['self'].split('/')
                
                sent['data'] = {}
                sent['data']['resource_uri'] = API_PATH + 'user_sentence/' + url[len(url)-1] + '/'
                sentenceArray.append(sent['data'])
                
            new_obj.__dict__['_data']['sentences'] = sentenceArray
            
            documents.append(new_obj)        
                
        return documents
    
    def obj_get_list(self, bundle, **kwargs):
        
        return self.get_object_list(bundle.request)
    
    def obj_get(self, bundle, **kwargs):
        
        gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)
        document = gdb.nodes.get(GRAPH_DATABASE_REST_URL + "node/" + kwargs['pk'] + '/')
        
        new_obj = DataObject(kwargs['pk'])
        new_obj.__dict__['_data'] = document.properties
        new_obj.__dict__['_data']['id'] = kwargs['pk']
        new_obj.__dict__['_data']['user'] = str(document.relationships.incoming(types=["owns"])[0].start.properties['username'])
        
        sentences = gdb.query("""MATCH (u:`User`)-[:owns]->(d:`UserDocument`)-[:sentences]->(s:`UserSentence`) WHERE d.CTS='""" +document.properties['CTS']+ """' RETURN DISTINCT s ORDER BY ID(s)""")
        sentenceArray = []
        for s in sentences:
            sent = s[0]
            url = sent['self'].split('/')
            # this might seems a little hacky, but API resources are very decoupled,
            # which gives us great performance instead of creating relations amongst objects and referencing/dereferencing foreign keyed fields
            sent['data']['resource_uri'] = API_PATH + 'user_sentence/' + url[len(url)-1] + '/'
            sentenceArray.append(sent['data'])
                
            new_obj.__dict__['_data']['sentences'] = sentenceArray

        # get a dictionary of related translations of this document
        relatedDocuments = gdb.query("""MATCH (d:`UserDocument`)-[:sentences]->(s:`UserSentence`)-[:words]->(w:`Word`)-[:translation]->(t:`Word`)<-[:words]-(s1:`Sentence`)<-[:sentences]-(d1:`Document`) WHERE HAS (d.CTS) AND d.CTS='""" + document.properties['CTS'] + """' RETURN DISTINCT d1 ORDER BY ID(d1)""")
        
        new_obj.__dict__['_data']['translations']={}
        for rd in relatedDocuments:
            doc = rd[0]
            url = doc['self'].split('/')
            if doc['data']['lang'] in CTS_LANG:
                new_obj.__dict__['_data']['translations'][doc['data']['lang']] = doc['data']
                new_obj.__dict__['_data']['translations'][doc['data']['lang']]['resource_uri']= API_PATH + 'document/' + url[len(url)-1] +'/'


        return new_obj
    
    
    # means csrftoken and sessionid  is required, if resource on session auth?!    
    def post_list(self, request, **kwargs):
        """
        Create a new document object and return it if the user is authenticated and exists. Create a new neo node in case the users doesn't exist on this side.
        """
        gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)
        
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        
        if not request.user or not request.user.is_authenticated():
            return self.create_response(request, { 'success': False, 'error_message': 'You are not authenticated, %s.' % request.user })

        data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))

        # get the user via neo look-up or create a newone
        if request.user.username is not None:
            userTable = gdb.query("""MATCH (u:`User`) WHERE HAS (u.username) AND u.username='""" + request.user.username + """' RETURN u""")
        
            if len(userTable) > 0:    
                userurl = userTable[0][0]['self']
                userNode = gdb.nodes.get(userurl)            
            
            else:
                userNode = gdb.nodes.create(username=request.user.username)
                userNode.labels.add("User")
            
            document = gdb.nodes.create(
                CTS = data.get("CTS"),  
                author = data.get("author"), 
                lang = data.get("lang"),    
                name = data.get("name")
            )
            document.labels.add("UserDocument")
            data['resource_uri'] = '/api/v1/user_document/' + str(document.id) + '/'
            data['user'] = request.user.username
            
            if document is None :
                # in case an error wasn't already raised             
                raise ValidationError('Document node could not be created.')
        
            # Form the connections from the new Submission node to the existing slide and user nodes
            userNode.owns(document)
                
            return self.create_response(request, data)
        
        else:
            return self.error_response(request, {'error': 'User is required.' }, response_class=HttpBadRequest)
