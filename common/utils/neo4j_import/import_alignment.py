# coding: utf8
from django.conf import settings
from neo4jrestclient.client import GraphDatabase
from xml.dom import minidom

################ set your alignment's meta data ################
# The script assumes Alpheios alignment output with the references being unique in the document
# It also assumes the Greek to alignment to be the first section in the xml.
# To adapt this, use alignNode.childNodes[1] and alignNode.childNodes[3] and 
# ANY_NODE.attributes['ANY_ATTRIBUTE_NAME'].value

xml_file = "align.xml"
document_CTS = "urn:cts:greekLit:tlg0003.tlg001.perseus-en"
document_CTS_greek = "urn:cts:greekLit:tlg0003.tlg001.perseus-grc"
target_lang = "en"
author_in_target_lang = "Thucydides"
work_in_taget_lang = "The Pentekontaetia"
host = "http://localhost:7474/db/data/"

################################################################

# graph database instance
gdb = GraphDatabase(host)

# create the document node at the very beginning
d = gdb.nodes.create(CTS=document_CTS, author=author_in_target_lang, name=work_in_taget_lang, lang=target_lang)
d.labels.add("Document") 

# xml parser instance
doc = minidom.parse(xml_file)

alignNode = doc.firstChild

counter = 0
for sent in alignNode.childNodes:

	# skip lang nodes
	if counter > 3 and counter%2 == 1:	
		# the two node sets for the two languages
		greekNodes = sent.childNodes[1].childNodes
		transNodes = sent.childNodes[3].childNodes
		
		# create the sentence node
		s = gdb.nodes.create(CTS=document_CTS + ":" + sent.attributes['id'].value)
		
		# handle the translated sentence
		wordcounter = 0
		for node in transNodes:
			# not interested in empty text nodes
			if node.attributes:
				wordcounter += 1
				# get word id
				word_id = node.attributes['n'].value
				# get the actual word string from the node "text"...
				textNode = node.childNodes[1]
				# ... and its inner text node
				word = textNode.childNodes[0].toxml()				
				
				# create the translated word node here
				w = gdb.nodes.create(CTS=document_CTS + ":" + word_id, value=word, length=len(word), lang=target_lang)
				w.labels.add("Word")
				# set the relationship to the sentence
				s.words(w)
				
				# get the ref node
				for n in node.childNodes:
					if n.attributes:
						ref_string_array = n.attributes['nrefs'].value.split(" ")
						# loop over references
						for ref in ref_string_array:
							 if not ref == "":
							 	# save the relationship, get the word node first
							 	table = gdb.query("""MATCH (w) WHERE w.CTS='""" + document_CTS_greek + ":" + ref + """' RETURN w""")
							 	greek_word = gdb.nodes.get(table[0][0]['self'])
							 	greek_word.translation(w)
							 	print "1) engl: " + str(w.id)
							 	print "2) greek: " + str(greek_word.id)
							 	
		
		# finish the translated sentence
		# assuming the basic Greek data is already there, no creation of Greek words happens here
		s.set('length', wordcounter)
		s.labels.add("Sentence")
		d.sentences(s)	
		
		# handle the Greek sentence
		for node in greekNodes:
			if node.attributes:
				# node is the word node
				# get word id ref
				word_id = node.attributes['n'].value
				# get the actual word string from the node "text"...
				#textNode = node.childNodes[1]
				# ... and its inner text node
				#word = textNode.childNodes[0].toxml()
				
				# get the word from the database
				qry = gdb.query("""MATCH (w) WHERE w.CTS='""" + document_CTS_greek + ":" + word_id + """' RETURN w""")
				greek_word = gdb.nodes.get(qry[0][0]['self'])
				
				# get the ref node
				for n in node.childNodes:
					if n.attributes:
						ref_string_array = n.attributes['nrefs'].value.split(" ")
						for ref in ref_string_array:
							 if not ref == "":
							 	# save the relationship, get the word node first
							 	table = gdb.query("""MATCH (w) WHERE w.CTS='""" + document_CTS + ":" + ref + """' RETURN w""")
							 	w = gdb.nodes.get(table[0][0]['self'])
							 	w.translation(greek_word)
							 	print "1) greek: " + str(greek_word.id)
							 	print "2) engl: " + str(w.id)
				
					
	counter = counter +1
