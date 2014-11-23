from phaidra.settings import GRAPH_DATABASE_REST_URL, API_PATH, ENABLE_WORD_LIST_SORTING

from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.resources import Resource
from tastypie.cache import SimpleCache

from neo4jrestclient.client import GraphDatabase

from app.models import Grammar

import json
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phaidra.settings")

# imported from the phaidra api
from validation import ResourceValidation
from utils import DataObject, sort_object_words


class WordResource(Resource):
    
    CTS = fields.CharField(attribute='CTS', null = True, blank = True)
    value = fields.CharField(attribute='value', null = True, blank = True)
    form = fields.CharField(attribute='form', null = True, blank = True)
    lemma = fields.CharField(attribute='lemma', null = True, blank = True)
    ref = fields.CharField(attribute='ref', null = True, blank = True)
    lang = fields.CharField(attribute='lang', null = True, blank = True)
    
    sentence_resource_uri = fields.CharField(attribute='sentence_resource_uri', null = True, blank = True)
    
    length = fields.IntegerField(attribute='length', null = True, blank = True)
    tbwid = fields.IntegerField(attribute='tbwid', null = True, blank = True)
    head = fields.IntegerField(attribute='head', null = True, blank = True)
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
    
    lemma_resource_uri = fields.CharField(attribute='lemma_resource_uri', null = True, blank = True)
    translations = fields.ListField(attribute='translations', null = True, blank = True)
    
    class Meta:
        object_class = DataObject
        resource_name = 'word'
        authorization = ReadOnlyAuthorization()
        cache = SimpleCache(timeout=None)
        validation =  ResourceValidation()

    
    def detail_uri_kwargs(self, bundle_or_obj):
        
        kwargs = {}        
        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.id
        else:
            kwargs['pk'] = bundle_or_obj.id
        return kwargs
    
    def get_object_list(self, request):
        
        gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)
        attrlist = ['lang','CTS', 'length', 'case', 'dialect', 'head', 'form', 'posClass', 'cid', 'gender', 'tbwid', 'pos', 'value', 'degree', 'number','lemma', 'relation', 'isIndecl', 'ref', 'posAdd', 'mood', 'tense', 'voice', 'person']
        words = []
        query_params = {}
        
        if request.GET.get('ref'):
                
            try:
                grammarParams = Grammar.objects.filter(ref=request.GET.get('ref'))[0].query.split('&')        
                for pair in grammarParams:
                    query_params[pair.split('=')[0]] = pair.split('=')[1]
            except KeyError as k:
                return words            
        
        # query by ordinary filters        
        for obj in request.GET.keys():
            if obj in attrlist and request.GET.get(obj) is not None:
                query_params[obj] = request.GET.get(obj)
            elif obj.split('__')[0] in attrlist and request.GET.get(obj) is not None:
                query_params[obj] = request.GET.get(obj)
        
        # implement filtering
        if len(query_params) > 0:
            
            # generate query
            q = """MATCH (s:`Sentence`)-[:words]->(w:`Word`) WHERE """
            
            # filter word on parameters
            for key in query_params:     
                # fuzzy match           
                if len(key.split('__')) > 1:
                    if key.split('__')[1] == 'contains':
                        # multi values
                        if "__" in query_params[key]:
                            q = q + """("""
                            chunks = query_params[key].split('__')
                            for chunk in chunks:
                                q = q + """ w."""+key.split('__')[0]+ """=~'.*""" +chunk+ """.*' OR """
                            q = q[:len(q)-3]
                            q = q + """) AND """
                        # one value
                        else:
                            q = q + """HAS (w.""" +key.split('__')[0]+ """) AND w.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """.*' AND """
                    elif key.split('__')[1] == 'startswith':
                        if "__" in query_params[key]:
                            q = q + """("""
                            chunks = query_params[key].split('__')
                            for chunk in chunks:
                                q = q + """ w."""+key.split('__')[0]+ """=~'""" +chunk+ """.*' OR """
                            q = q[:len(q)-3]
                            q = q + """) AND """
                        else:
                            q = q + """HAS (w.""" +key.split('__')[0]+ """) AND w.""" +key.split('__')[0]+ """=~'""" +query_params[key]+ """.*' AND """
                    elif key.split('__')[1] == 'endswith':
                        if "__" in query_params[key]:
                            q = q + """("""
                            chunks = query_params[key].split('__')
                            for chunk in chunks:
                                q = q + """ w."""+key.split('__')[0]+ """=~'.*""" +chunk+ """' OR """
                            q = q[:len(q)-3]
                            q = q + """) AND """
                        else:
                            q = q + """HAS (w.""" +key.split('__')[0]+ """) AND w.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """' AND """
                    # only for integer values
                    elif key.split('__')[1] == 'gt':
                        q = q + """HAS (w.""" +key.split('__')[0]+ """) AND w.""" +key.split('__')[0]+ """>""" +query_params[key]+ """ AND """
                    # only for integer values
                    elif key.split('__')[1] == 'lt':
                        q = q + """HAS (w.""" +key.split('__')[0]+ """) AND w.""" +key.split('__')[0]+ """<""" +query_params[key]+ """ AND """        
                    # negated match
                    elif key.split('__')[1] == 'isnot':
                        # integer values
                        if key.split('__')[0] in ['tbwid', 'head', 'length', 'cid']:
                            # multiple values
                            if "__" in query_params[key]:   
                                q = q + """("""
                                chunks = query_params[key].split('__')
                                for chunk in chunks:
                                    q = q + """ w."""+key.split('__')[0]+ """<>""" +chunk+ """ OR """
                                q = q[:len(q)-3]
                                q = q + """) AND """
                            # one value
                            else:
                                q = q + """HAS (w.""" +key.split('__')[0]+ """) AND w.""" +key.split('__')[0]+ """<>""" +query_params[key]+ """ AND """
                        # string values
                        else:
                            # multi values
                            if "__" in query_params[key]:   
                                q = q + """("""
                                chunks = query_params[key].split('__')
                                for chunk in chunks:
                                    q = q + """ w."""+key.split('__')[0]+ """<>'""" +chunk+ """' OR """
                                q = q[:len(q)-3]
                                q = q + """) AND """
                            # one value
                            else:
                                q = q + """HAS (w.""" +key.split('__')[0]+ """) AND w.""" +key.split('__')[0]+ """<>'""" +query_params[key]+ """' AND """
                # perfect match
                else:
                    # integer values
                    if key in ['tbwid', 'head', 'length', 'cid']:
                        # multi values
                        if "__" in query_params[key]:   
                                q = q + """("""
                                chunks = query_params[key].split('__')
                                for chunk in chunks:
                                    q = q + """ w."""+key.split('__')[0]+ """=""" +chunk+ """ OR """
                                q = q[:len(q)-3]
                                q = q + """) AND """
                        # one value
                        else:
                            q = q + """HAS (w.""" +key+ """) AND w.""" +key+ """=""" +query_params[key]+ """ AND """
                    # string values
                    else:
                        if "__" in query_params[key]:
                            q = q + """("""
                            chunks = query_params[key].split('__')
                            for chunk in chunks:
                                q = q + """ w."""+key.split('__')[0]+ """='""" +chunk+ """' OR """
                            q = q[:len(q)-3]
                            q = q + """) AND """
                        else:
                            q = q + """HAS (w.""" +key+ """) AND w.""" +key+ """='""" +query_params[key]+ """' AND """
            q = q[:len(q)-4]
            q = q + """RETURN w, s ORDER BY ID(w)"""
            
            table = gdb.query(q)
            
            # create the objects which was queried for and set all necessary attributes
            for t in table:
                word = t[0]
                sentence = t[1]        
                url = word['self'].split('/')
                urlSent = sentence['self'].split('/')        
                    
                new_obj = DataObject(url[len(url)-1])
                new_obj.__dict__['_data'] = word['data']        
                new_obj.__dict__['_data']['id'] = url[len(url)-1]
                new_obj.__dict__['_data']['sentence_resource_uri'] = API_PATH + 'sentence/' + urlSent[len(urlSent)-1] +'/'
                        
                words.append(new_obj)
            
            if ENABLE_WORD_LIST_SORTING:
                return sort_object_words(words[:500]) 
            else:
                return words
            #return words   
        
        # default querying on big dataset (CTS required)
        elif request.GET.get('document_CTS'):    

            # delted this so our word list is smaller
            #documentTable = gdb.query("""MATCH (n:`Document`) RETURN n ORDER BY ID(n)""")    
            #for d in documentTable:
            #document = d[0]
            wordTable = gdb.query("""MATCH (d:`Document`)-[:sentences]->(s:`Sentence`)-[:words]->(w:`Word`) WHERE d.CTS = '""" + request.GET.get('document_CTS') + """' RETURN w,s ORDER BY ID(w)""")
                            
            # get sent id
            for w in wordTable:
                word = w[0]
                sentence = w[1]
                url = word['self'].split('/')
                urlSent = sentence['self'].split('/')    
                        
                new_obj = DataObject(url[len(url)-1])
                new_obj.__dict__['_data'] = word['data']
                                    
                new_obj.__dict__['_data']['id'] = url[len(url)-1]
                new_obj.__dict__['_data']['sentence_resource_uri'] = API_PATH + 'sentence/' + urlSent[len(urlSent)-1] +'/'
                                    
                words.append(new_obj)
            
            if ENABLE_WORD_LIST_SORTING:
                return sort_object_words(words[:500]) 
            else:
                return words
        # no parameter for filtering, return empty
        else:
            return words
        
    
    def obj_get_list(self, bundle, **kwargs):
                
        dict = self._meta.validation.is_valid(bundle, bundle.request)
        if len(dict) > 0:
            return dict
        else:
            return self.get_object_list(bundle.request)
    
    
    def obj_get(self, bundle, **kwargs):
        
        gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)
        word = gdb.nodes.get(GRAPH_DATABASE_REST_URL + "node/" + kwargs['pk'] + '/')
        
        # ge the data of the word
        new_obj = DataObject(kwargs['pk'])
        new_obj.__dict__['_data'] = word.properties
        new_obj.__dict__['_data']['id'] = kwargs['pk']
        new_obj.__dict__['_data']['sentence_resource_uri'] = API_PATH + 'sentence/' + str(word.relationships.incoming(types=["words"])[0].start.id) + '/'
        
        # get the lemma
        lemmaRels = word.relationships.incoming(types=["values"])
        if len(lemmaRels) > 0:
            new_obj.__dict__['_data']['lemma_resource_uri'] = API_PATH + 'lemma/' + str(lemmaRels[0].start.id) + '/'
            
        translations = gdb.query("""MATCH (d:`Word`)-[:translation]->(w:`Word`) WHERE d.CTS='""" +word.properties['CTS']+ """' RETURN DISTINCT w ORDER BY ID(w)""")
        translationArray = []
        for t in translations:
            trans = t[0]
            url = trans['self'].split('/')
            trans['data']['resource_uri'] = API_PATH + 'word/' + url[len(url)-1] + '/'
            translationArray.append(trans['data'])
                
        new_obj.__dict__['_data']['translations'] = translationArray
                
        return new_obj


 
