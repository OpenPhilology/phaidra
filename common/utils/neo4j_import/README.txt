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


Initial Data
#########################################

# The treebank xml file of Francesco Mambrini 1999.01.0199_utf8.xml
# slightly changed by Greta Franzini when some data errors occured at the pre-proc step.
data/1999.01.0199_utf8_edited.xml

# A section of the Morpheus output of the whole Thucydides with some entries 
# manipulated to fit the sentence strucure of the treebank file of Mambrini.
data/thucmorphs_outtakes_edited.txt


The Morpho-Syntactic Data Dump and Import
#########################################

# This file contains the data as it was formerly fed into the neo database via some java code.
# This code took into consideration: the , the and the 
data/pentecontaetia_dump.json

# Script to export the databases document -, sentence -, word - and lemma nodes (of Pentecontaetia for now).
# the output of this script is the pentecontaetia_dump.json in the data directory.
pentecontaetia_export.py
# the script to import the docuemt -, sentence -, word - and lemma objects from the JSON dump (Pentecontaetia for now).
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

# If you are only interested in saving the treebank data of Thucydide's Pentecontaetia, run this script
import_treebank.py


General New Text Data import script
#########################################

# This script gives you an example how graph nodes should be built for adding new text into the graph database.
# It requires sentences to be linewise and punctuation to be separated.
import_any_text.py






