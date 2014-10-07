from phaidra.settings import GRAPH_DATABASE_REST_URL, API_PATH

from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.resources import Resource
from tastypie.cache import SimpleCache

from neo4jrestclient.client import GraphDatabase

# imported from the phaidra api
from validation import ResourceValidation
from utils import DataObject     


class LemmaResource(Resource):
    
    CITE = fields.CharField(attribute='CITE')
    value = fields.CharField(attribute='value')
    posAdd = fields.CharField(attribute='posAdd', null = True, blank = True)
    frequency = fields.IntegerField(attribute='frequency', null = True, blank = True)    
    values = fields.ListField(attribute='values', null = True, blank = True)
    
    class Meta:
        object_class = DataObject    
        resource_name = 'lemma'        
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
        attrlist = ['CITE', 'value', 'posAdd', 'frequency']
        lemmas = []
        
        query_params = {}
        for obj in request.GET.keys():
            if obj in attrlist and request.GET.get(obj) is not None:
                query_params[obj] = request.GET.get(obj)
            elif obj.split('__')[0] in attrlist and request.GET.get(obj) is not None:
                query_params[obj] = request.GET.get(obj)
        
        # implement filtering
        if len(query_params) > 0:
            
            # generate query
            q = """MATCH (l:`Lemma`)-[:values]->(w:`Word`) WHERE """
            
            # filter word on parameters
            for key in query_params:
                if len(key.split('__')) > 1:
                    if key.split('__')[1] == 'contains':
                        q = q + """HAS (l.""" +key.split('__')[0]+ """) AND l.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """.*' AND """
                    elif key.split('__')[1] == 'startswith':
                        q = q + """HAS (l.""" +key.split('__')[0]+ """) AND l.""" +key.split('__')[0]+ """=~'""" +query_params[key]+ """.*' AND """
                    elif key.split('__')[1] == 'endswith':
                        q = q + """HAS (l.""" +key.split('__')[0]+ """) AND l.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """' AND """
                    elif key.split('__')[1] == 'isnot':
                        if key == 'frequency':
                            q = q + """HAS (l.""" +key.split('__')[0]+ """) AND l.""" +key.split('__')[0]+ """<>""" +query_params[key]+ """ AND """
                        else:
                            q = q + """HAS (l.""" +key.split('__')[0]+ """) AND l.""" +key.split('__')[0]+ """<>'""" +query_params[key]+ """' AND """
                    elif key.split('__')[1] == 'gt':
                        q = q + """HAS (l.""" +key.split('__')[0]+ """) AND l.""" +key.split('__')[0]+ """>""" +query_params[key]+ """ AND """
                    elif key.split('__')[1] == 'lt':
                        q = q + """HAS (l.""" +key.split('__')[0]+ """) AND l.""" +key.split('__')[0]+ """<""" +query_params[key]+ """ AND """
                else:
                    if key == 'frequency':
                        q = q + """HAS (l.""" +key+ """) AND l.""" +key+ """=""" +query_params[key]+ """ AND """
                    else:
                        q = q + """HAS (l.""" +key+ """) AND l.""" +key+ """='""" +query_params[key]+ """' AND """
            q = q[:len(q)-4]
            q = q + """RETURN DISTINCT l ORDER BY ID(l)"""
            
            table = gdb.query(q)
        
        # default querying    
        else:    
            table = gdb.query("""MATCH (l:`Lemma`)-[:values]->(w:`Word`) WHERE HAS (l.CITE) RETURN DISTINCT l ORDER BY ID(l)""")
            
        # create the objects which was queried for and set all necessary attributes
        for t in table:
            lemma = t[0]    
            url = lemma['self'].split('/')        
                
            new_obj = DataObject(url[len(url)-1])
            new_obj.__dict__['_data'] = lemma['data']        
            new_obj.__dict__['_data']['id'] = url[len(url)-1]
            
            # get the word as a node to query relations
            lemmaNode = gdb.nodes.get(lemma['self'])
            
            values = lemmaNode.relationships.outgoing(types=["values"])    
            valuesArray = []
            for v in range(0, len(values), 1):
                val = values[v].end
                val.properties['resource_uri'] = API_PATH + 'word/' + str(val.id) + '/'
                valuesArray.append(val.properties)

            new_obj.__dict__['_data']['values'] = valuesArray            
            lemmas.append(new_obj)
                
        return lemmas
    
    def obj_get_list(self, bundle, **kwargs):
        
        dict = self._meta.validation.is_valid(bundle, bundle.request)
        if len(dict) > 0:
            return dict
        else:
            return self.get_object_list(bundle.request)
    
    def obj_get(self, bundle, **kwargs):
        
        gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)
        lemma = gdb.nodes.get(GRAPH_DATABASE_REST_URL + "node/" + kwargs['pk'] + '/')
        
        # ge the data of the word
        new_obj = DataObject(kwargs['pk'])
        new_obj.__dict__['_data'] = lemma.properties
        new_obj.__dict__['_data']['id'] = kwargs['pk']
        
        # get the values    
        values = lemma.relationships.outgoing(types=["values"])            
        valuesArray = []
        for v in range(0, len(values), 1):
            val = values[v].end
            val.properties['resource_uri'] = API_PATH + 'word/' + str(val.id) + '/'
            val.properties['translations'] = []

            # get the full translation # force API into full representation if cache is enabled
            if bundle.request.GET.get('full'):    
                
                translations = gdb.query("""MATCH (d:`Word`)-[:translation]->(w:`Word`) WHERE d.CTS='""" + val.properties['CTS'] + """' RETURN DISTINCT w ORDER BY ID(w)""")
                translationArray = []
                for t in translations:
                    trans = t[0]
                    transurl = trans['self'].split('/')
                    trans['data']['resource_uri'] = API_PATH + 'word/' + transurl[len(transurl)-1] + '/'
                    translationArray.append(trans['data'])
                    val.properties['translations'] = translationArray
            
            valuesArray.append(val.properties)
            
        new_obj.__dict__['_data']['values'] = valuesArray

        return new_obj