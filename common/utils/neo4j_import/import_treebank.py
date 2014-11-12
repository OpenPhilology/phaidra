# coding: utf8
from neo4jrestclient.client import GraphDatabase
from xml.dom import minidom
import json
import os

################ set your xml's meta data #####################

treebank_file_name = "data/1999.01.0199_utf8_edited.xml"
host = "http://localhost:7474/db/data/"
document_cts = "urn:cts:greekLit:tlg0003.tlg001.perseus-grc"
work_author = "Θουκυδίδης"
work_title = "Πεντηκονταετία"
work_language = "grc"

################################################################

def decode_morphology(morphological_code):
    
    dictionary = {}
    # morph codes are assumably ordered
    morph_list = ['pos', 'person', 'number', 'tense', 'mood', 'voice', 'gender', 'case', 'degree']
    i = -1
    for code in morph_list:
        i = i+1
        try:
            dictionary[code] = morph_content[code][morphological_code[i]]
        except KeyError as k:
            continue
    return dictionary
    
################################################################

# globals
path = os.path.dirname(os.path.abspath(__file__))
treebank_file = os.path.join(path, treebank_file_name)
morph_code_file = os.path.join(path, "morph_codes.json")
gdb = GraphDatabase(host)

morph_content = {}
with open(morph_code_file, 'r') as json_data:
    morph_content = json.load(json_data)
    json_data.close()
    
# create the document
d = gdb.nodes.create(CTS=document_cts,
                     author=work_author,
                     title=work_title,
                     lang=work_language) 

d.labels.add("Document")   
    
# get first node from the xml parser instance
alignNode = minidom.parse(treebank_file).firstChild

chapter_old = 0
sent_no = 0
# run over sentences
for sentence in alignNode.childNodes: 
    sentence_string = ""
    
    # no text nodes 
    if sentence.attributes and sentence.tagName == 'sentence':
        
        sent_no = sent_no+1
        # get sentence meta here
        subdoc = sentence.attributes['subdoc'].value.split(':')
        book = int(subdoc[0].split('=')[1])
        chapter = int(subdoc[1].split('=')[1])
        if chapter != chapter_old:
            sent_no = 1
            chapter_old = chapter
        
        # create the sentence node
        s = gdb.nodes.create() 
        s.labels.add("Sentence")
        s['CTS'] = document_cts + ":" + str(book) + "." + str(chapter) + "." + str(sent_no)
        print document_cts + ":" + str(book) + "." + str(chapter) + "." + str(sent_no)
        
        # run over word nodes
        word_no = 0
        for word in sentence.childNodes:
            
            if word.attributes and word.tagName == 'word':
                
                sentence_string = sentence_string + " " + word.attributes['form'].value
                word_no = word_no+1
                word_dict = {'cid': word.attributes['cid'].value,
                        'value': word.attributes['form'].value,
                        'head': word.attributes['head'].value,
                        'tbwid': word.attributes['id'].value,
                        'lemma': word.attributes['lemma'].value,
                        'relation': word.attributes['relation'].value} 
                               
                morph = decode_morphology(word.attributes['postag'].value)                
                #print document_cts + ":" + str(book) + "." + str(chapter) + "." + str(sent_no) + ":" + str(word_no)
                
                w = gdb.nodes.create()
                w.labels.add("Word")
                
                # xml node attributes
                for attr in word_dict:
                    w[attr] = word_dict[attr]
                    
                # decoded morph codes
                for key in morph:
                    w[key] = morph[key]
                    
                w['length'] = len(word_dict['value'])
                w['CTS'] = document_cts + ":" + str(book) + "." + str(chapter) + "." + str(sent_no) + ":" + str(word_no)
                s.words(w)
        
        s['sentence'] = sentence_string
        s['length'] = word_no
        d.sentences(s)
                    
                    
# build indexes at the end:
gdb.query("""CREATE INDEX ON :Document(CTS)""")
gdb.query("""CREATE INDEX ON :Document(ID)""")
gdb.query("""CREATE INDEX ON :Sentence(CTS)""")
gdb.query("""CREATE INDEX ON :Sentence(ID)""")
gdb.query("""CREATE INDEX ON :Word(CTS)""")
gdb.query("""CREATE INDEX ON :Word(ID)""")
gdb.query("""CREATE INDEX ON :Lemma(CITE)""")
gdb.query("""CREATE INDEX ON :Lemma(ID)""")
                
            
            
            










            