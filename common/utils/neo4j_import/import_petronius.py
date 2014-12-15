# coding: utf8
from neo4jrestclient.client import GraphDatabase
from xml.dom import minidom
import json
import os
import re

################ set your xml's meta data #####################

xml_file_name = "data/phi0972.phi001.perseus-lat1_excerpt_tokenized.xml"
host = "http://localhost:7474/db/data/"
document_cts = "phi0972.phi001.perseus-lat"
work_author = "Petronius"
work_title = "Satyricon"
work_language = "lat"
# last signs of a sentence
endings = ['.', '?', ';']

################################################################


# globals
path = os.path.dirname(os.path.abspath(__file__))
xml_file = os.path.join(path, xml_file_name)


# create the graph database instance
gdb = GraphDatabase(host)
    
# create the document
d = gdb.nodes.create(CTS=document_cts,
                     author=work_author,
                     name=work_title,
                     lang=work_language) 

d.labels.add("Document")   
    
# get first node from the xml parser instance
body = minidom.parse(xml_file).firstChild.childNodes[1]

global_counter = 0
sentence_no = 0
chapter_no = 0
book_no = 1
current_sentence = ''
list = []
# run over milestones
for ms in body.childNodes: 
     
    # get the text info of a milestone
    if ms.nodeValue and len(ms.nodeValue.strip()) > 0:
        chapter_no = chapter_no + 1
        sentence_no = 1
        
        text = ms.nodeValue.strip()
        
        # read the words of the text of a milestone
        word_counter = 0
        for word in re.split(" +", text):
            
            #create the sentence
            current_sentence = current_sentence + word + ' '
            
            # if word is upper and sentence is not empty and beginning of a milestone, delete last word, save the sentence set the new word
            if word[0].isupper() and len(current_sentence[:-len(word)-1]) > 0 and word_counter == 0:
                current_sentence = current_sentence[:-len(word)-1]
                
                sentence_no_tmp = list[global_counter-1]["sn"]+1
                chapter_no_tmp = list[global_counter-1]["cn"]
              
                # compose the sentence cts and save the sentence
                sentence_cts = document_cts + ':' + str(book_no) + '.' + str(chapter_no_tmp) + '.' + str(sentence_no_tmp)
                list.append({sentence_cts: current_sentence, "sn":sentence_no_tmp, "cn": chapter_no_tmp})
                
                global_counter = global_counter +1                        
                #print sentence_cts + ": " + current_sentence         
                current_sentence = word + ' '
                           
            
            # save the sentence ordinarily
            elif word in endings:
                
                # compose the sentence cts and save the sentence
                sentence_cts = document_cts + ':' + str(book_no) + '.' + str(chapter_no) + '.' + str(sentence_no)
                list.append({sentence_cts:current_sentence, "sn":sentence_no, "cn": chapter_no})
                
                global_counter = global_counter +1
                #print sentence_cts + ": " + current_sentence
                current_sentence = ''
                        
                sentence_no = sentence_no + 1
                

            # increase word counter of a milestone   
            word_counter = word_counter + 1
            
            
# handle the last sentence containing no ending            
sentence_no = list[global_counter-1]["sn"]+1
chapter_no = list[global_counter-1]["cn"]                    
sentence_cts = document_cts + ':' + str(book_no) + '.' + str(chapter_no) + '.' + str(sentence_no)
list.append({sentence_cts: current_sentence, "sn":sentence_no, "cn": chapter_no})
global_counter = global_counter +1               
#print sentence_cts + ": " + current_sentence



# now create the neo data objects
for sent in list:
    
    for key in sent:
        if not key == "sn" and not key == "cn":
            
            s = gdb.nodes.create(CTS=key, sentence=sent[key])
            s.labels.add("Sentence")
    
            word_no = 0
            for w in sent[key].split(' '):
                if len(w) >= 1:
                    word_no = word_no + 1
                    cts = document_cts + ':' + str(book_no) + '.' + str(sent["cn"]) + '.' + str(sent["sn"]) + ':' + str(word_no)
                    w = gdb.nodes.create(CTS=cts, value=w, length=len(w))
                    w.labels.add("Word")
                    s.words(w)
            s['length'] = word_no
            d.sentences(s)
            
            print "Sentence: " + key + " saved to database." + " len: " + str(word_no)
            
            
            
            
            
            
            