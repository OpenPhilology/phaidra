from neo4jrestclient.client import GraphDatabase
import json

################ set your dump's meta data #####################

dump_file = "pentecontaetia_dump.json"
host = "http://localhost:7474/db/data/"

################################################################

# graph database instance
gdb = GraphDatabase(host)

filename = dump_file
fileContent = {}

with open(filename, 'r') as json_data:
    fileContent = json.load(json_data)
    json_data.close()
    
    # create the document node
    d = gdb.nodes.create()
    d.labels.add('Document')
    for doc_attr in fileContent:
        if not doc_attr == 'sentences':
            d[doc_attr] = fileContent[doc_attr]
            
        else:
            sentences = fileContent[doc_attr]
            for sentence in sentences:
                
                # create the sentence node
                s = gdb.nodes.create() 
                s.labels.add("Sentence")
                for sent_attr in sentence:
                    
                    if not sent_attr == 'words':
                         s[sent_attr] = sentence[sent_attr]
                    
                    else:
                        words = sentence[sent_attr]
                        for word in words:
                            
                            # create the word node
                            w = gdb.nodes.create() 
                            w.labels.add("Word")
                            for word_attr in word:
                    
                                if not word_attr == 'lemma':
                                    w[word_attr] = word[word_attr]
                                    
                                elif word_attr == 'lemma' and  len(word[word_attr]) > 0:
                                    if word[word_attr]['CITE'] != '':                             
                                        CITE = word[word_attr]['CITE']
                                        table = gdb.query("""MATCH (l:`Lemma`) WHERE l.CITE='""" + "bla" + """' RETURN l""")
                                        try:
                                            lemma = gdb.nodes.get(table[0][0]['self'])
                                        except:
                                            # create the lemma node
                                            l = gdb.nodes.create()
                                            l.labels.add("Lemma")
                                            for lemma_attr in word[word_attr]:
                                                if lemma_attr == 'value':
                                                    w['lemma'] = word[word_attr][lemma_attr]
                                                l[lemma_attr] = word[word_attr][lemma_attr]
                                        w.lemma(l)
                                else:
                                    w[word_attr] = ''
                            s.words(w)           
                d.sentences(s)
                print "Sentence: " + s['CTS'] + " saved."
                        
                                        
                                        
                                
        
                                 
                                 
                                 