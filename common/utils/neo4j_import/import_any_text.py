# coding: utf8
from neo4jrestclient.client import GraphDatabase
#from xml.dom import minidom
import json
import os

################ set your xml's meta data #####################

file_name = "data/text.txt"
host = "http://localhost:7474/db/data/"
document_cts = "urn:cts:greekLit:tlg0815.tlg001.perseus-lat"
work_author = "Authorname"
work_title = "Worktitle"
work_language = "lat"

################################################################

# globals
path = os.path.dirname(os.path.abspath(__file__))
treebank_file = os.path.join(path, file_name)

# create the graph database instance
gdb = GraphDatabase(host)
      
# reject if the document already exists    
doc_name = gdb.query("""MATCH (d) WHERE d.CTS='""" + document_cts + """' RETURN d.name""")  
if len(doc_name) >= 1:
    print "Document " + str(doc_name[0][0].encode('utf-8')) + " already exists."
    quit()
    
# create the document node
d = gdb.nodes.create(CTS=document_cts,
                     author=work_author,
                     name=work_title,
                     lang=work_language) 

d.labels.add("Document") 
    
# open the file
file = open('data/text.txt', 'r')

# set your sentence ends here
sentence_ends = ['.', '·', '!', '?']

sentence_no = 1
chapter_no = 1
book_no = 1
current_sentence = ''

# run over lines of the file
for line in file:    
    line = line.strip()
    
    for word in line.split(" "):
        # append the next word of the file to the current sentence string 
        current_sentence = current_sentence + word + ' '
        
        # if the end of a sentence was reached
        if word in sentence_ends:
            current_sentence = current_sentence.strip()
            # node creation etc. has to happen here to give more flexibility to the sentence behavior in the file
            # compose the sentence cts
            sentence_cts = document_cts + ':' + str(book_no) + '.' + str(chapter_no) + '.' + str(sentence_no)
            # create the sentence node with attributes
            s = gdb.nodes.create(CTS=sentence_cts,
                                 sentence=current_sentence,
                                 length=len(current_sentence.split(' ')))
            # set the label of the sentence to enable indices
            s.labels.add("Sentence")
            # set the relation between document and sentence node
            d.sentences(s)   
            print "Sentence: " + sentence_cts + " saved to database."
                               
            word_no = 0
            for w in current_sentence.split(' '):
                word_no = word_no + 1
                # compose the word cts
                cts = document_cts + ':' + str(book_no) + '.' + str(chapter_no) + '.' + str(sentence_no) + ':' + str(word_no)
                # create the word node with the attributes
                w = gdb.nodes.create(CTS=cts, value=w, length=len(w))
                # set the label of the word to enable indices
                w.labels.add("Word")
                # set the relation between sentence and word node
                s.words(w)
                      
            #  increase the sentence_no, reset the sentence
            sentence_no = sentence_no + 1
            current_sentence = '' 
            
            
              
        
     
                    
                    

                
            
            
            










            