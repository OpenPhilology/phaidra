#################### Data used in the Neo4j Database ####################
# This File describes the texts and data formats that were used or pre- #
# processed to fit into the Neo4j database of the application.          #
# Additionally the scripts contained in this directory and their use    #
# will be described.                                                    #
#########################################################################


#########################################################################
# Text and data files used for initially pre-processing to fit the data #
# into the data base.                                                   # 
#########################################################################


Initial Data Formats
#########################################

# The treebank xml file of Francesco Mambrini 1999.01.0199_utf8.xml
# slightly changed by Greta Franzini when some data errors occured at the pre-proc step.
data/1999.01.0199_utf8_edited.xml

# A section of the Morpheus output of the whole Thucydides with some entries 
# manipulated to fit the sentence structure of the treebank file of Mambrini.
data/thucmorphs_outtakes_edited.txt


The Morpho-Syntactic Data Dump and Import
#########################################

# This file contains the data as it was formerly fed into the neo database via some java code.
# This code took into consideration: the 1999.01.0199_utf8_edited.xml, the thucmorphs_outtakes_edited.txt and the alignment data as it was avaialable.
# The pentecontaetia_dump now contains the document node of the Pentecontaetia, the Sentence, Word and Lemma nodes and the ralationships amongst them all.
data/pentecontaetia_dump.json

# Script to export the databases document -, sentence -, word - and lemma nodes (of Pentecontaetia for now).
# The output of this script is the opt/phaidra/common/utils/neo4j_import/data/pentecontaetia_dump.json.
pentecontaetia_export.py
# the script to import the document -, sentence -, word - and lemma objects from the JSON dump (Pentecontaetia for now).
pentecontaetia_import.py


The Alignment Import
#########################################

# The script to import alignment data (assuming the import of the dump was done)
import_alignment.py

# The used and supported aligment xml files which can be run (assuming the import ot the dump was done) by the fabfile.py as:
# fab import_alignment:lang='all' or fab import_alignment:lang='en'
data/tlg0003.tlg001.perseus-grc.xml
data/tlg0003.tlg001.perseus-eng.xml
data/tlg0003.tlg001.perseus-hrv.xml


The User - and Submission Dump and Import
#########################################

# This file contains the dumped data from a test user submission set
data/submission_dump.json

# Script to save all current users and their related submissions from a current neo4j database.
# There is also information saved to set the relations between a user and the words he knows the grammar of (knows_grammar=[]), 
# the lemmas he knows (knows_vocab_lemmas=[]) and the words he knows (knows_vocab_words={}) next to the number he encountered this word.
# the output of this script is the submission_dump.json in the data directory.
submission_export.py
# the script to import the submission of all users from the JSON dump.
submission_import.py


The Only Treebank Import
#########################################

# If you are only interested in having the treebank data of Thucydide's Pentecontaetia (next to morphological infos, but without the information Morpheus provides), run this script
import_treebank.py


General New Text Data Import Script
#########################################

# This script gives you an example how graph nodes should be built for adding new text into the graph database.
# It requires punctuation to be separated. The example text is in data/text.txt
import_any_text.py

# the example text
data/text.txt


Delete a Work (Recommended for only! testing purposes)
#########################################

# If you want to delete a subgraph, e.g. a work, because of data updating issues, run the following command either in the Neo4j browser
# (localhost:7474/browser) or it's old data browser (under http://localhost:7474/webadmin/).
# (This is only recommended as long as no user submissions were made based on this work!)
# Start by checking your subgraph:

MATCH (d:`Document`)-[dr:`sentences`]->(s:`Sentence`)-[sr:`words`]->(w:`Word`)
WHERE d.CTS='urn:cts:greekLit:tlg0815.tlg001.perseus-lat'
RETURN d, dr, s, sr, w

# DELETE it afterwards. !!! Caution !!! The author of this text gives no guaranty on any global or local database inconsistencies or misbehaviors or unrecoverable data afterwards!
# It is also highly recommended to NOT delete nodes on a production system, if indexing is switched on, because of ID reuse, which leads to challenging sorting algorithms.
# See the API docu in the project wiki for further detail on sorting.
MATCH (d:`Document`)-[dr:`sentences`]->(s:`Sentence`)-[sr:`words`]->(w:`Word`)
WHERE d.CTS='urn:cts:greekLit:tlg0815.tlg001.perseus-lat'
DELETE d, dr, s, sr, w


General New XML Data Import - Petronius
#########################################
# The original XML file with Petronius' literature in.
data/phi0972.phi001.perseus-lat1.xml

# The file manipulated by Giuseppe G. A. Celano to get rid of several xml tags.
data/phi0972.phi001.perseus-lat1_simplified.xml

# The Petronius file from Giuseppe, containing only the 1st part (w/o Fragmenta and Poems), and already tokenized.
data/phi0972.phi001.perseus-lat1_excerpt.xml

# The import script for data/phi0972.phi001.perseus-lat1_excerpt_tokenized.xml
import_petronius.py



