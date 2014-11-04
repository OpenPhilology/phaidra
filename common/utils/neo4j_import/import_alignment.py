# coding: utf8
#from django.conf import settings
from neo4jrestclient.client import GraphDatabase
from xml.dom import minidom
import os

################ set your alignment's meta data ################
# The script assumes Alpheios alignment output with the references being unique in the document
# It assumes Greek to be the L1 language.

TARGET_LANGUAGE = 'fa'

class Document:
    path = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, author, title, lang, locale, primary_source_urn):
        self.author = author
        self.title = title
        self.lang = lang
        self.locale = locale
        self.primary_source_urn = primary_source_urn
    
    def cts(self):
        return 'urn:cts:greekLit:tlg0003.tlg001.perseus-%s' % self.locale

    def xml(self):
        xml_file = 'tlg0003.tlg001.perseus-%s.xml' % self.lang
        return os.path.join(self.path, xml_file)

languages = {
    'en': Document('Thucydides', 'The Pentecontaetia', 'eng', 'en', 
        'urn:cts:greekLit:tlg0003.tlg001.perseus-grc'),
    'fa': Document('ﺕﻮﺳیﺩیﺩ', 'ﺕﺍﺭیﺥ پﻦﺟﺎﻫ ﺱﺎﻟ گﺬﺸﺘﻫ', 'fas', 'fa', 
        'urn:cts:greekLit:tlg0003.tlg001.perseus-grc'),
    'hr': Document('Tukidid', 'Povijest Peloponeskograta', 'hrv', 'hr',
        'urn:cts:greekLit:tlg0003.tlg001.perseus-grc')
}

################################################################

def save_sentence(nodes, sentence_ref, lang):
    
    wordcounter = 0
    referring_CTS_root = ''
    
    if lang == 'grc':
        referring_CTS_root = document.cts()
    # create the sentence node of the translation
    else:
        referring_CTS_root = document.primary_source_urn
        s = gdb.nodes.create(CTS=document.cts() + ":" + sentence_ref)
        
    for node in nodes:
        # not interested in empty text nodes
        if node.attributes and node.tagName == 'w':
            wordcounter = wordcounter + 1
            # get the actual word value from the text node of the <text> node of the <w> node.
            word_value = node.childNodes[1].childNodes[0].toxml()                
                
            # get the (greek) word from the database or create the word as a node if it from an L2 language
            if lang == 'grc': 
                wordTable = gdb.query("""MATCH (w) WHERE w.CTS='""" + document.primary_source_urn + ":" + node.attributes['n'].value + """' RETURN w""")
                w = gdb.nodes.get(wordTable[0][0]['self'])
            else:
                w = gdb.nodes.create(CTS=document.cts() + ":" + node.attributes['n'].value, value=word_value, length=len(word_value), lang=document.lang)
                w.labels.add("Word")
                s.words(w)
                              
            # get the referring translations
            try:
                array = node.childNodes[3].attributes['nrefs'].value.split(" ")
                # loop over references
                for ref in array:
                    if not ref == "":
                        table = gdb.query("""MATCH (w) WHERE w.CTS='""" + referring_CTS_root + ":" + ref + """' RETURN w""")
                        translated_word = gdb.nodes.get(table[0][0]['self'])
                        w.translation(translated_word)
                        print "word: " + node.attributes['n'].value + "; word_id: " + str(w.id)
                        print "ref: " + ref + "; ref_word_id: " + str(translated_word.id)
            
            except:
                continue
        
    # finish the creation of the translated sentence and save it to the document  
    if lang != 'grc':           
        s.set('length', wordcounter)
        s.labels.add("Sentence")
        d.sentences(s)  

################################################################

document = languages[TARGET_LANGUAGE]

host = "http://localhost:7474/db/data/"

# graph database instance
gdb = GraphDatabase(host)

# create the document node at the very beginning
d = gdb.nodes.create(CTS=document.cts(), 
        author=document.author, 
        name=document.title, 
        lang=document.locale)

d.labels.add("Document") 

# get first node from the xml parser instance
alignNode = minidom.parse(document.xml()).firstChild
 
for sentence in alignNode.childNodes:
    
    # avoid the language nodes at the very beginning 
    if sentence.attributes and sentence.tagName == 'sentence':	
		# get the two node sets for the two languages after ensuring the order of the parsed alignments
        if sentence.childNodes[1].attributes['lnum'].value == 'L1':
            save_sentence(sentence.childNodes[3].childNodes, sentence.attributes['id'].value, 'translation')
            save_sentence(sentence.childNodes[1].childNodes, sentence.attributes['id'].value, 'grc')
        else:
            save_sentence(sentence.childNodes[1].childNodes, entence.attributes['id'].value, 'translation')
            save_sentence(sentence.childNodes[3].childNodes, entence.attributes['id'].value, 'grc')
        
        





 

		

				
					

          
