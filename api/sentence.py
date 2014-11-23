from phaidra.settings import CTS_LANG
from phaidra.settings import GRAPH_DATABASE_REST_URL, API_PATH

from django.core.cache import cache

from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.exceptions import BadRequest
from tastypie.resources import Resource

from neo4jrestclient.client import GraphDatabase

# imported from the phaidra api
from validation import ResourceValidation
from utils import DataObject, sort_sentences, sort_words


class SentenceResource(Resource):
    
    CTS = fields.CharField(attribute='CTS', null = True, blank = True)
    sentence = fields.CharField(attribute='sentence', null = True, blank = True)    
    length = fields.IntegerField(attribute='length', null = True, blank = True)
    document_resource_uri = fields.CharField(attribute='document_resource_uri', null = True, blank = True)
    words = fields.ListField(attribute='words', null = True, blank = True)
    translations = fields.DictField(attribute='translations', null = True, blank = True)
    
    class Meta:
        object_class = DataObject
        resource_name = 'sentence'    
        authorization = ReadOnlyAuthorization()    
        # cache = SimpleCache(timeout=None) # caching is not that easy for this resource, caching inline
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
            q = """MATCH (d:`Document`)-[:sentences]->(s:`Sentence`) WHERE """
            
            # filter word on parameters
            for key in query_params:                    
                if len(key.split('__')) > 1:
                    if key.split('__')[1] == 'contains':
                        q = q + """HAS (s.""" +key.split('__')[0]+ """) AND s.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """.*' AND """
                    elif key.split('__')[1] == 'startswith':
                        q = q + """HAS (s.""" +key.split('__')[0]+ """) AND s.""" +key.split('__')[0]+ """=~'""" +query_params[key]+ """.*' AND """
                    elif key.split('__')[1] == 'endswith':
                        q = q + """HAS (s.""" +key.split('__')[0]+ """) AND s.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """' AND """
                    elif key.split('__')[1] == 'gt':
                        q = q + """HAS (s.""" +key.split('__')[0]+ """) AND s.""" +key.split('__')[0]+ """>""" +query_params[key]+ """ AND """
                    elif key.split('__')[1] == 'lt':
                        q = q + """HAS (s.""" +key.split('__')[0]+ """) AND s.""" +key.split('__')[0]+ """<""" +query_params[key]+ """ AND """    
                    elif key.split('__')[1] == 'isnot':
                        if key.split('__')[0] == 'length':
                            q = q + """HAS (s.""" +key.split('__')[0]+ """) AND s.""" +key.split('__')[0]+ """<>""" +query_params[key]+ """ AND """
                        else:
                            q = q + """HAS (s.""" +key.split('__')[0]+ """) AND s.""" +key.split('__')[0]+ """<>'""" +query_params[key]+ """' AND """
                else:
                    if key == 'length':
                        q = q + """HAS (s.""" +key+ """) AND s.""" +key+ """=""" +query_params[key]+ """ AND """
                    else:
                        q = q + """HAS (s.""" +key+ """) AND s.""" +key+ """='""" +query_params[key]+ """' AND """
            q = q[:len(q)-4]
            q = q + """RETURN s, d ORDER BY ID(s)"""
            
            table = gdb.query(q)
        
        # default querying    
        else:    
            table = gdb.query("""MATCH (d:`Document`)-[:sentences]->(s:`Sentence`) WHERE HAS (s.CTS) RETURN s, d ORDER BY ID(s)""")
            
        # create the objects which was queried for and set all necessary attributes
        for t in table:
            sentence = t[0]
            document = t[1]        
            url = sentence['self'].split('/')
            urlDoc = document['self'].split('/')        
                
            new_obj = DataObject(url[len(url)-1])
            new_obj.__dict__['_data'] = sentence['data']        
            new_obj.__dict__['_data']['id'] = url[len(url)-1]
            new_obj.__dict__['_data']['document_resource_uri'] = API_PATH + 'document/' + urlDoc[len(urlDoc)-1] +'/'
            sentences.append(new_obj)
                
        return sort_sentences(sentences)
    
    def obj_get_list(self, bundle, **kwargs):
        
        dict = self._meta.validation.is_valid(bundle, bundle.request)
        if len(dict) > 0:
            return dict
        else:
            return self.get_object_list(bundle.request)
    
    def obj_get(self, bundle, **kwargs):
        
        # get the actually cached objects 
        if cache.get("sentence_%s"%kwargs['pk']) is not None and not bundle.request.GET.get('full') and not bundle.request.GET.get('short'):
            return cache.get("sentence_%s"%kwargs['pk'])
        
        elif bundle.request.GET.get('short') and not bundle.request.GET.get('full') and cache.get("sentence_short_%s"%kwargs['pk']) is not None:
            return cache.get("sentence_short_%s"%kwargs['pk'])
        
        elif bundle.request.GET.get('full') and not bundle.request.GET.get('short') and cache.get("sentence_full_%s"%kwargs['pk']) is not None:
            return cache.get("sentence_full_%s"%kwargs['pk'])
        
        elif cache.get("sentence_full_short%s"%kwargs['pk']) is not None and not bundle.request.GET.get('full') and not bundle.request.GET.get('short'):
            return cache.get("sentence_full_short_%s"%kwargs['pk'])
    
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
            
        # get the sentence parameters            
        new_obj = DataObject(kwargs['pk'])
        new_obj.__dict__['_data'] = sentence.properties
        new_obj.__dict__['_data']['id'] = kwargs['pk']
        new_obj.__dict__['_data']['document_resource_uri'] = API_PATH + 'document/' + str(sentence.relationships.incoming(types=["sentences"])[0].start.id) + '/'
        
        # get a dictionary of related translation of this sentence 
        relatedSentences = gdb.query("""MATCH (s:`Sentence`)-[:words]->(w:`Word`)-[:translation]->(t:`Word`)<-[:words]-(s1:`Sentence`) WHERE HAS (s.CTS) AND s.CTS='"""+ sentence.properties['CTS'] + """' RETURN DISTINCT s1 ORDER BY ID(s1)""")
    
        new_obj.__dict__['_data']['translations']={}
        for rs in relatedSentences:
            sent = rs[0]
            url = sent['self'].split('/')
            for lang in CTS_LANG:
                if sent['data']['CTS'].find("-"+lang+":") != -1:
                    new_obj.__dict__['_data']['translations'][lang] = API_PATH + 'sentence/' + url[len(url)-1] +'/'        
        
        # get the words and lemma resource uri of the sentence    
        words = gdb.query("""MATCH (d:`Sentence`)-[:words]->(w:`Word`) WHERE d.CTS='""" +sentence.properties['CTS']+ """' RETURN DISTINCT w ORDER BY ID(w)""")
        wordArray = []
        for w in words:
            word = w[0]
            url = word['self'].split('/')
            word['data']['resource_uri'] = API_PATH + 'word/' + url[len(url)-1] + '/'
            wordNode = gdb.nodes.get(GRAPH_DATABASE_REST_URL + "node/" + url[len(url)-1] + '/')
            
            # get the lemma    
            lemmaRels = wordNode.relationships.incoming(types=["values"])
            if len(lemmaRels) > 0:
                word['data']['lemma_resource_uri'] = API_PATH + 'lemma/' + str(lemmaRels[0].start.id) + '/'
            
            # get the translations of a word if parameter is set
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
            
        wordArray = sort_words(wordArray)
            
        # if short=True return only words of the short sentence
        if bundle.request.GET.get('short'):

            wordArray = self.shorten(wordArray, query_params)
            if wordArray is None:
                #return None
                raise BadRequest("Sentence doesn't hit your query.")
        
        
        new_obj.__dict__['_data']['words'] = wordArray
        
        # deal with caching here -> all are different objects
        if bundle.request.GET.get('full') and bundle.request.GET.get('short'):    
            if cache.get("sentence_full_short_%s"%kwargs['pk']) is None:
                cache.set("sentence_full_short_%s"%kwargs['pk'], new_obj, None)
        
        if bundle.request.GET.get('short'):                    
            if cache.get("sentence_short_%s"%kwargs['pk']) is None:
                cache.set("sentence_short_%s"%kwargs['pk'], new_obj, None)
                
        elif bundle.request.GET.get('full'):
            if cache.get("sentence_full_%s"%kwargs['pk']) is None:
                cache.set("sentence_full_%s"%kwargs['pk'], new_obj, None)
            
        else:
            if cache.get("sentence_%s"%kwargs['pk']) is None:    
                cache.set("sentence_%s"%kwargs['pk'], new_obj, None)

        return new_obj
    
    
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
            if w['head'] != 0:
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
                                #aim_words.append(w.value) # Is are checked later
                    
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
                    
                # refinement of u coords # i want u if i is not empty
                for id in u:
                    for id2 in i:
                        w = nodes[id2].value
                        if w['head'] == id:
                            aim_words.append(w)
                    if len(i) > 0:
                        w2 = nodes[id].value
                        aim_words.append(w2)
                          
                            
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
                                return sorted(aim_words, key=lambda x: x['tbwid'])    
                        
                        return None        
                    else:        
                        # set and order words
                        return sorted(aim_words, key=lambda x: x['tbwid'])                
                    
                    # set and order words
                    return sorted(aim_words, key=lambda x: x['tbwid'])
                                    
        return None
