# coding: utf8
from neo4jrestclient.client import GraphDatabase
import json
import os

################ set your dump's meta data #####################

path = os.path.dirname(os.path.abspath(__file__))
dump_file = os.path.join(path, "data/submission_dump.json")
host = "http://localhost:7474/db/data/"

################################################################

# graph database instance
gdb = GraphDatabase(host)

filename = dump_file
fileContent = {}

with open(filename, 'r') as json_data:
    fileContent = json.load(json_data)
    json_data.close()

for user in fileContent:
    
    # create the submission node
    u = gdb.nodes.create(username=user)
    u.labels.add('User')
    
    # save the submissions
    for sub in fileContent[user]['submissions']:
        
        s = gdb.nodes.create()
        s.labels.add('Submission')
        u.submits(s)
        # handle submission attributes
        for sub_attr in sub:
            
            # create a list before handle encounteres words attribute
            if sub_attr == 'encounteredWords':
                enc_words = []
                for cts in sub[sub_attr]:
                    enc_words.append(cts)
                s[sub_attr] = enc_words
                print enc_words
            else:
                s[sub_attr] = sub[sub_attr]
                print sub[sub_attr]
         
    # set links to the words   
    for voc in fileContent[user]['knows_vocab_words']:
        
        table = gdb.query("""MATCH (w:`Word`) WHERE HAS (w.CTS) and w.CTS='""" + voc +"""' RETURN w""")           
        word = gdb.nodes.get(table[0][0]['self'])
        u.knows_vocab(word, times_seen=fileContent[user]['knows_vocab_words'][voc])
        print str(user) + " knows voc of word " + str(word['CTS']) + " and saw it " + str(fileContent[user]['knows_vocab_words'][voc]) + " time(s)"
    
    # set links to the lemmas   
    for voc in fileContent[user]['knows_vocab_lemmas']:
        
        table = gdb.query("""MATCH (l:`Lemma`) WHERE HAS (l.CITE) and l.CITE='""" + voc +"""' RETURN l""")           
        lemma = gdb.nodes.get(table[0][0]['self'])
        u.knows_vocab(lemma)
        print str(user)  + " knows voc of lemma: " + str(lemma['CITE'].encode('utf-8'))
        
    # set links to the words where grammar was known  
    for word in fileContent[user]['knows_grammar']:
        
        table = gdb.query("""MATCH (w:`Word`) WHERE HAS (w.CTS) and w.CTS='""" + word +"""' RETURN w""")           
        word = gdb.nodes.get(table[0][0]['self'])
        u.knows_grammar(word)
        print str(user)  + " knows grammar of word: " + str(word['CTS'])
            
                      
# build indexes at the end:
gdb.query("""CREATE INDEX ON :Submission(ID)""")
gdb.query("""CREATE INDEX ON :User(ID)""")
gdb.query("""CREATE INDEX ON :User(username)""")
                                        
                                        
                                
        
                                 
                                 
                                 
