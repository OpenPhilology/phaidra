# coding: utf8
from neo4jrestclient.client import GraphDatabase
import json

################ set your dump's meta data #####################

dump_file = "data/submission_dump.json"
host = "http://localhost:7474/db/data/"

################################################################

# graph database instance
gdb = GraphDatabase(host)
file = open(dump_file, 'w')
global_dict={}

# query for the users
table = gdb.query("""MATCH (u:`User`) RETURN u.username""")
# get the user
for user in table:
    user = user[0]
    user_dict = {}

    # get his submissions
    submission_array = []
    submission_table = gdb.query("""MATCH (u:`User`)-[:submits]->(s:`Submission`) WHERE u.username='""" + user + """' RETURN s""")   
    for sub in submission_table:
        submission = sub[0]
        submissionNode = gdb.nodes.get(submission['self'])     
        submission_array.append(submissionNode.properties)
    
    user_dict['submissions'] = submission_array


    # get the words a user knows the grammar of
    grammar_list = []   
    word_table = gdb.query("""MATCH (u:`User`)-[:knows_grammar]->(w:`Word`) WHERE u.username='""" + user + """' RETURN w.CTS""")  
    for w in word_table:
        grammar_list.append(w[0])
        
    user_dict['knows_grammar'] = grammar_list
    
    
    #get the words a user knows vocab of 
    vocab_list = {}
    word_table = gdb.query("""MATCH (u:`User`)-[kv:knows_vocab]->(w:`Word`) WHERE u.username='""" + user + """' RETURN w.CTS, kv""")
    for w in word_table:
        vocab_list[w[0]] = w[1]['data']['times_seen']
        
    user_dict['knows_vocab_words'] = vocab_list
    
    
    # get the lemma a user knows vocab of
    vocab_list = []
    lemma_table = gdb.query("""MATCH (u:`User`)-[:knows_vocab]->(l:`Lemma`) WHERE u.username='""" + user + """' RETURN l.CITE""")
    for l in lemma_table:
        vocab_list.append(l[0])
        
    user_dict['knows_vocab_lemmas'] = vocab_list


    # dump to the main dict  
    global_dict[user] = user_dict 
    
    
# dump all data    
j = json.dumps(global_dict, sort_keys=True, indent=4, encoding="utf-8")
print >> file, j

file.close()