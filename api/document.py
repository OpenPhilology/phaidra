from phaidra.settings import CTS_LANG
from phaidra.settings import GRAPH_DATABASE_REST_URL, API_PATH

from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.resources import Resource
from tastypie.cache import SimpleCache

from neo4jrestclient.client import GraphDatabase

# imported from the phaidra api
from validation import ResourceValidation
from utils import DataObject, sort_sentences


class DocumentResource(Resource):
    
    CTS = fields.CharField(attribute='CTS')
    lang = fields.CharField(attribute='lang', null = True, blank = True)    
    sentences = fields.ListField(attribute='sentences', null = True, blank = True)
    name = fields.CharField(attribute='name', null = True, blank = True)
    author = fields.CharField(attribute='author', null = True, blank = True)
    translations = fields.DictField(attribute='translations', null = True, blank = True)
    
    class Meta:
        object_class = DataObject
        resource_name = 'document'    
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
            q = """MATCH (d:`Document`)-[:sentences]->(s:`Sentence`) WHERE """
            
            # filter word on parameters
            for key in query_params:
                if len(key.split('__')) > 1:
                    if key.split('__')[1] == 'contains':
                        q = q + """HAS (d.""" +key.split('__')[0]+ """) AND d.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """.*' AND """
                    elif key.split('__')[1] == 'startswith':
                        q = q + """HAS (d.""" +key.split('__')[0]+ """) AND d.""" +key.split('__')[0]+ """=~'""" +query_params[key]+ """.*' AND """
                    elif key.split('__')[1] == 'endswith':
                        q = q + """HAS (d.""" +key.split('__')[0]+ """) AND d.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """' AND """
                    elif key.split('__')[1] == 'isnot':
                        q = q + """HAS (d.""" +key.split('__')[0]+ """) AND d.""" +key.split('__')[0]+ """<>'""" +query_params[key]+ """' AND """
                else:
                    q = q + """HAS (d.""" +key+ """) AND d.""" +key+ """='""" +query_params[key]+ """' AND """
            q = q[:len(q)-4]
            q = q + """RETURN DISTINCT d ORDER BY ID(d)"""
            
            table = gdb.query(q)
        
        # default querying    
        else:    
            table = gdb.query("""MATCH (d:`Document`) RETURN DISTINCT d ORDER BY ID(d)""")
            
        # create the objects which was queried for and set all necessary attributes
        for t in table:
            document = t[0]        
            urlDoc = document['self'].split('/')        
                
            new_obj = DataObject(urlDoc[len(urlDoc)-1])
            new_obj.__dict__['_data'] = document['data']        
            new_obj.__dict__['_data']['id'] = urlDoc[len(urlDoc)-1]
        
            sentences = gdb.query("""MATCH (d:`Document`)-[:sentences]->(s:`Sentence`) WHERE d.CTS='""" +document['data']['CTS']+ """' RETURN DISTINCT s ORDER BY ID(s)""")
            sentenceArray = []
            for s in sentences:
                
                sent = s[0]
                url = sent['self'].split('/')
                sent_cts = sent['data']['CTS']
                sent['data'] = {}
                sent['data']['resource_uri'] = API_PATH + 'sentence/' + url[len(url)-1] + '/'
                sent['data']['CTS'] = sent_cts
                sentenceArray.append(sent['data'])
                
            new_obj.__dict__['_data']['sentences'] = sort_sentences(sentenceArray)
            
            documents.append(new_obj)        
                
        return documents
    
    def obj_get_list(self, bundle, **kwargs):
        
        dict = self._meta.validation.is_valid(bundle, bundle.request)
        if len(dict) > 0:
            return dict
        else:
            return self.get_object_list(bundle.request)
    
    
    def obj_get(self, bundle, **kwargs):
        
        gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)
        document = gdb.nodes.get(GRAPH_DATABASE_REST_URL + "node/" + kwargs['pk'] + '/')
        
        new_obj = DataObject(kwargs['pk'])
        new_obj.__dict__['_data'] = document.properties
        new_obj.__dict__['_data']['id'] = kwargs['pk']
        
        sentences = gdb.query("""MATCH (d:`Document`)-[:sentences]->(s:`Sentence`) WHERE d.CTS='""" +document.properties['CTS']+ """' RETURN DISTINCT s ORDER BY ID(s)""")
        sentenceArray = []
        for s in sentences:
            sent = s[0]
            url = sent['self'].split('/')
            # this might seems a little hacky, but API resources are very decoupled,
            # which gives us great performance instead of creating relations amongst objects and referencing/dereferencing foreign keyed fields
            sent['data']['resource_uri'] = API_PATH + 'sentence/' + url[len(url)-1] + '/'
            sentenceArray.append(sent['data'])

        new_obj.__dict__['_data']['sentences'] = sort_sentences(sentenceArray)
            
        
        # get a dictionary of related translations of this document
        relatedDocuments = gdb.query("""MATCH (d:`Document`)-[:sentences]->(s:`Sentence`)-[:words]->(w:`Word`)-[:translation]->(t:`Word`)<-[:words]-(s1:`Sentence`)<-[:sentences]-(d1:`Document`) WHERE HAS (d.CTS) AND d.CTS='"""+ document.properties['CTS'] +"""' RETURN DISTINCT d1 ORDER BY ID(d1)""")
        
        new_obj.__dict__['_data']['translations']={}
        for rd in relatedDocuments:
            doc = rd[0]
            url = doc['self'].split('/')
            if doc['data']['lang'] in CTS_LANG:
                new_obj.__dict__['_data']['translations'][doc['data']['lang']] = doc['data']
                new_obj.__dict__['_data']['translations'][doc['data']['lang']]['resource_uri']= API_PATH + 'document/' + url[len(url)-1] +'/'


        return new_obj
