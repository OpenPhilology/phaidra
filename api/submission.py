#from __future__ import unicode_literals
from phaidra.settings import GRAPH_DATABASE_REST_URL

from django.core.exceptions import ValidationError

from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.authentication import SessionAuthentication, BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.http import HttpBadRequest, HttpUnauthorized
from tastypie.exceptions import BadRequest, Unauthorized
from tastypie.resources import Resource
from tastypie.cache import SimpleCache

from neo4jrestclient.client import GraphDatabase

from app.models import Grammar

import json
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phaidra.settings")

# imported from the phaidra api
from validation import ResourceValidation
from utils import DataObject
  

class SubmissionAuthorization(Authorization):
    
    def read_list(self, object_list, bundle):
        
        gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)        
        attrlist = ['response', 'task', 'ref', 'user', 'starttime', 'timestamp', 'accuracy']
        
        query_params = {}
        for obj in bundle.request.GET.keys():
            if obj in attrlist and bundle.request.GET.get(obj) is not None:
                query_params[obj] = bundle.request.GET.get(obj)
            elif obj.split('__')[0] in attrlist and bundle.request.GET.get(obj) is not None:
                query_params[obj] = bundle.request.GET.get(obj)
                
        # implement filtering
        if len(query_params) > 0:
                        
            # generate query
            q = """MATCH (u:`User`)-[:submits]->(s:`Submission`) WHERE """
            
            # filter word on parameters
            for key in query_params:                
                if len(key.split('__')) > 1:
                    if key.split('__')[1] == 'contains':
                        q = q + """HAS (s.""" +key.split('__')[0]+ """) AND s.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """.*' AND """
                    elif key.split('__')[1] == 'startswith':
                        q = q + """HAS (s.""" +key.split('__')[0]+ """) AND s.""" +key.split('__')[0]+ """=~'""" +query_params[key]+ """.*' AND """
                    elif key.split('__')[1] == 'endswith':
                        q = q + """HAS (s.""" +key.split('__')[0]+ """) AND s.""" +key.split('__')[0]+ """=~'.*""" +query_params[key]+ """' AND """
                    elif key.split('__')[1] == 'isnot':
                        if key.split('__')[0] == 'accuracy':
                            q = q + """HAS (s.""" +key.split('__')[0]+ """) AND s.""" +key.split('__')[0]+ """<>""" +query_params[key]+ """ AND """
                        else:
                            q = q + """HAS (s.""" +key.split('__')[0]+ """) AND s.""" +key.split('__')[0]+ """<>'""" +query_params[key]+ """' AND """
                    elif key.split('__')[1] == 'gt':
                        q = q + """HAS (s.""" +key.split('__')[0]+ """) AND s.""" +key.split('__')[0]+ """>""" +query_params[key]+ """ AND """
                    elif key.split('__')[1] == 'lt':
                        q = q + """HAS (s.""" +key.split('__')[0]+ """) AND s.""" +key.split('__')[0]+ """<""" +query_params[key]+ """ AND """
                else:
                    if key == 'accuracy':
                        q = q + """HAS (s.""" +key+ """) AND s.""" +key+ """=""" +query_params[key]+ """ AND """
                    else:
                        q = q + """HAS (s.""" +key+ """) AND s.""" +key+ """='""" +query_params[key]+ """' AND """
            q = q[:len(q)-4]
            q = q + """RETURN s"""
            
            table = gdb.query(q)
    
        # ordinary querying
        else:    
            table = gdb.query("""MATCH (u:`User`)-[:submits]->(s:`Submission`) WHERE HAS (u.username) AND u.username='""" + bundle.request.user.username + """' RETURN s""")        
                
        # create the objects which was queried for and set all necessary attributes
        submissions = []
        for s in table:
            submission = s[0]    
            url = submission['self'].split('/')                        
            new_obj = DataObject(url[len(url)-1])
            new_obj.__dict__['_data'] = submission['data']        
            new_obj.__dict__['_data']['id'] = url[len(url)-1]
            new_obj.__dict__['_data']['user'] = bundle.request.user.username                        
            submissions.append(new_obj)
                
        return submissions
    
    def read_detail(self, object_list, bundle):
        
        if bundle.request.user is not None:
            return object_list                
        else:
            raise Unauthorized()
    
    ### not in use yet. User submissions are related to the user in the sent data, which makes sure the the user was already verified
    def create_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user
        
      
class SubmissionResource(Resource):
    
    response = fields.CharField(attribute='response', null = True, blank = True) 
    task = fields.CharField(attribute='task', null = True, blank = True)
    ref = fields.CharField(attribute='ref', null = True, blank = True)
    starttime = fields.CharField(attribute='starttime', null = True, blank = True)
    accuracy = fields.IntegerField(attribute='accuracy', null = True, blank = True)
    encounteredWords = fields.ListField(attribute='encounteredWords', null = True, blank = True)
    timestamp = fields.CharField(attribute='timestamp', null = True, blank = True)
    user = fields.CharField(attribute='user', null = True, blank = True)
    
    class Meta:
        object_class = DataObject
        resource_name = 'submission'
        allowed_methods = ['post', 'get', 'patch']
        authentication = BasicAuthentication() 
        authorization = SubmissionAuthorization()
        cache = SimpleCache(timeout=None)
        validation =  ResourceValidation()

    def detail_uri_kwargs(self, bundle_or_obj):
        
        kwargs = {}    
        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.id    
        else:
            kwargs['pk'] = bundle_or_obj.id        
        return kwargs

    # means csrftoken and sessionid  is required for reading, if resource on session auth?!
    def authorized_read_list(self, object_list, bundle):
        """
        Handles checking of permissions to see if the user has authorization
        to GET this resource.
        """
    
        try:
            auth_result = self._meta.authorization.read_list(object_list, bundle)
        except Unauthorized as e:
            self.unauthorized_result(e)
            
        return auth_result
    
    
    def obj_get_list(self, bundle, **kwargs):
        
        dict = self._meta.validation.is_valid(bundle, bundle.request)
        if len(dict) > 0:
            return dict
        else:                
            try:
                return self.authorized_read_list(bundle.request, bundle)
            except ValueError:
                raise BadRequest("Invalid resource lookup data provided (mismatched type).")
    
    
    def obj_get(self, bundle, **kwargs):
        
        gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)
        submission = gdb.nodes.get(GRAPH_DATABASE_REST_URL + "node/" + kwargs['pk'] + '/')
            
        new_obj = DataObject(kwargs['pk'])
        new_obj.__dict__['_data'] = submission.properties
        new_obj.__dict__['_data']['id'] = kwargs['pk']
            
        try:
            auth_result = self._meta.authorization.read_detail(new_obj, bundle)
        except Unauthorized as e:
            self.unauthorized_result(e)

        return auth_result    
      
    def post_list(self, request, **kwargs):
        """
        Create a new submission object, which relates to the slide it responds to and the user who submitted it.
        Return the submission object, complete with whether or not they got the answer correct.
        """
        gdb = GraphDatabase(GRAPH_DATABASE_REST_URL)
        
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        
        if not request.user or not request.user.is_authenticated():
            return self.error_response(request, { 'success': False, 'error_message': 'You are not authenticated, %s.' % request.user }, response_class=HttpUnauthorized)

        data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))

        # get the user via neo look-up or create a newone
        if request.user.username is not None:
            userTable = gdb.query("""MATCH (u:`User`)-[:submits]->(s:`Submission`) WHERE HAS (u.username) AND u.username='""" + request.user.username + """' RETURN u""")
            
            if len(userTable) > 0:
                userurl = userTable[0][0]['self']
                userNode = gdb.nodes.get(userurl)
            
            else:
                userNode = gdb.nodes.create(username=request.user.username)
                userNode.labels.add("User")
                
            # create the submission        
            subms = gdb.nodes.create(
                response = data.get("response"),
                task = data.get("task"), 
                ref = data.get("ref"),    # string
                starttime = data.get("starttime"),     # catch this so that it doesn't lead to submission problems
                accuracy = int(data.get("accuracy")),
                encounteredWords = data.get("encounteredWords"), # array
                timestamp = data.get("timestamp") 
            )
            
            subms.labels.add("Submission")
            
            if subms is None :
                # in case an error wasn't already raised             
                raise ValidationError('Submission node could not be created.')
            
            # Form the connections from the new Submission node to the existing slide and user nodes
            userNode.submits(subms)
            
            # check empty encountered words than spare the 
            for cts in data.get("encounteredWords"):
                if not cts:
                    body = json.loads(request.body) if type(request.body) is str else request.body
                    return self.create_response(request, body)
            
            # set links between the ref key filtered words and the user... 
            q = """MATCH (w:`Word`) WHERE """
            try:
                grammarParams = Grammar.objects.filter(ref=data.get("ref"))[0].query.split('&')
                for pair in grammarParams:
                    if len(pair.split('=')[0].split('__')) == 1:
                        attribute = pair.split('=')[0]
                        value= pair.split('=')[1]
                        q = q + """HAS (w.""" +attribute+ """) AND w.""" +attribute+ """='""" +value+ """' AND """
                    elif len(pair.split('=')[0].split('__')) > 1:
                        attribute = pair.split('=')[0].split('__')[0]
                        operator = pair.split('=')[0].split('__')[1]
                        value= pair.split('=')[1]
                        if operator == 'contains':
                            q = q + """HAS (w.""" +attribute+ """) AND w.""" +attribute+ """=~'.*""" +value+ """.*' AND """
                        elif operator == 'startswith':
                            q = q + """HAS (w.""" +attribute+ """) AND w.""" +attribute+ """=~'""" +value+ """.*' AND """
                        elif operator == 'endswith':
                            q = q + """HAS (w.""" +attribute+ """) AND w.""" +attribute+ """=~'.*""" +value+ """' AND """
                        elif operator == 'isnot':
                            q = q + """HAS (w.""" +attribute+ """) AND w.""" +attribute+ """<>'""" +value+ """' AND """
                q = q[:len(q)-4]
                q = q + """RETURN w"""        
            except:
                return self.error_response(request, {'error': 'Reference data could not be processed.' }, response_class=HttpBadRequest)
            
            # ... if not already known
            table = gdb.query(q)
            for t in table:
                word = gdb.nodes.get(t[0]['self'])
                knows_morph = gdb.query("""MATCH (u:`User`)-[kg:knows_morph]->(w:`Word`) WHERE HAS (w.CTS) AND w.CTS='""" + t[0]['data']['CTS'] + """' RETURN kg""")
                if len(knows_morph) < 1:
                    userNode.knows_morph(word)              
                            
            # set links between the lemmas of the encountered words (as vocab knowledge) and the words themselves, if the encountered words were not already known, otherwise increase times_seen
            for cts in data.get("encounteredWords"):    
                relation = gdb.query("""MATCH (u:`User`)-[kv:has_seen]->(w:`Word`)
                                        WHERE HAS (w.CTS) and w.CTS='""" + cts +"""' and u.username='""" + request.user.username + """' RETURN kv""")
                try:
                   times = relation[0][0]['data']['times_seen']+1
                   id = relation[0][0]['self'].split('/')[len(relation[0][0]['self'].split('/'))-1]  
                   rel = gdb.relationships.get(id)
                   rel.properties = {'times_seen':times}      
                except IndexError as e:   
                    table = gdb.query("""MATCH (l:`Lemma`)-[:values]->(w:`Word`) WHERE HAS (w.CTS) and w.CTS='""" + cts +"""' RETURN w, l""")
                    try:
                        word = gdb.nodes.get(table[0][0]['self'])
                        lemma = gdb.nodes.get(table[0][1]['self'])
                        userNode.has_seen(word, times_seen=1)
                        userNode.has_seen(lemma)
                    except IndexError as e:
                        # no relationship between word and lemma means punctuation
                        continue
                    
            # create the body
            body = json.loads(request.body) if type(request.body) is str else request.body
            
            return self.create_response(request, body)
        else:
            return self.error_response(request, {'error': 'User is required.' }, response_class=HttpBadRequest)
        
        
        
        
