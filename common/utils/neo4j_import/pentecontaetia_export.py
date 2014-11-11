# coding: utf8
from neo4jrestclient.client import GraphDatabase
import json

################ set your dump's meta data #####################

dump_file = "data/pentecontaetia_dump.json"
# the CTS of the document that is going to be dumped;
dump_document_CTS = "urn:cts:greekLit:tlg0003.tlg001.perseus-grc"
host = "http://localhost:7474/db/data/"

################################################################

# graph database instance
gdb = GraphDatabase(host)
file = open(dump_file, 'w')

# query for the document
q = """MATCH (d:`Document`) WHERE d.CTS='""" + dump_document_CTS + """' RETURN d"""
table = gdb.query(q)

document_dict = {}
for doc in table:
	document = doc[0]
	documentNode = gdb.nodes.get(document['self'])
	#print documentNode.properties

	# get the metas of the document
	for doc_attr in documentNode.properties:
		document_dict[doc_attr] = documentNode.properties[doc_attr]
	
	#senteceRels = documentNode.relationships.outgoing(types=["sentences"])
	sent_table = gdb.query("""MATCH (d:`Document`)-[:sentences]->(s:`Sentence`) WHERE d.CTS='"""+ documentNode.properties['CTS'] +"""' RETURN s ORDER BY ID(s)""")

	#get the document's sentences
	sentences_array = []
	for sent in sent_table:
		sentence = sent[0]
		sentenceNode = gdb.nodes.get(sentence['self'])
		# get the sentence metas
		sentence_dict = {}
		for sent_attr in sentenceNode.properties:
			sentence_dict[sent_attr] = sentenceNode.properties[sent_attr]

		#wordRels = sent.end.relationships.outgoing(types=["words"])
		w_table = gdb.query("""MATCH (s:`Sentence`)-[:words]->(w:`Word`) WHERE s.CTS='"""+ sentenceNode.properties['CTS'] +"""' RETURN w ORDER BY ID(w)""")

		#get the sentence's words
		words_array = []
		for w in w_table:
			word = w[0]
			wordNode = gdb.nodes.get(word['self'])
			# get the word metas
			word_dict = {}
			for word_attr in wordNode.properties:
				word_dict[word_attr] = wordNode.properties[word_attr]

			lemmaRels = wordNode.relationships.incoming(types=["values"])
				
			# get the lemma of a word
			lemma_dict = {}
			if len(lemmaRels) > 0:
				for lemma_attr in lemmaRels[0].start.properties:
					lemma_dict[lemma_attr] = lemmaRels[0].start.properties[lemma_attr]
			
			# save the lemma as a word attribute and append the word to the sentence's word array
			word_dict['lemma'] = lemma_dict
			words_array.append(word_dict)

		# save the word array as sentence attribute and append the sentence dict to the document's sentences array
		sentence_dict['words'] = words_array
		sentences_array.append(sentence_dict)
		
		print "Sentence: " + sentence_dict['CTS'] + " dumped."
	# save the sentence array as document attribute
	document_dict['sentences'] = sentences_array

	# dump the file	
	j = json.dumps(document_dict, sort_keys=True, indent=4, encoding="utf-8")

	print >> file, j

file.close()

		













