from django.db import models
from django.utils.text import slugify

class Textbook(models.Model):
	name = models.CharField(max_length=200)
	source_lang = models.CharField(max_length=2)
	target_lang = models.CharField(max_length=2)

	def __unicode__(self):
<<<<<<< HEAD
		return unicode(self.name) or u''

class Sentence(models.NodeModel):
	# introduced to get API filed work
	internal = models.StringProperty(max_length=200)
	CTS = models.StringProperty(max_length=200)
	sentence = models.StringProperty()
	length = models.IntegerProperty()
	document = models.Relationship(Document,
                                rel_type='belongs_to',
                                single=True,
                                related_name='sentences'
				#preserve_ordering=True
                               )
	
	def word_objects(self):
		array = []
		for obj in reversed(self.words.all()):
			array.append(obj)
		return array
	
	def get_shortened(self, params = None):
					
		words = self.words.all()
		
		# interrupt as soon as possible if there is no according syntactical information available
		if words[0].head is None:
			return None
			
		#fo = open("foo.txt", "wb")
		#millis = int(round(time.time() * 1000))
		#fo.write("%s filter words and build tree: \n" % millis)
			
		# save words within a map for faster lookup			
		dataMap = dict((word.tbwid, word) for word in words)				
		#build tree structure		
		dataTree = {0:'root','children':[]}
		
		for word in words:
			if word.head == 0 or word.relation == 'PRED' or word.relation == 'PRED_CO':					
				dataTree['children'].append(word)			
			else:
				head = dataMap[word.head]
				if head is not None:
						if head.children is not None:
							head.children.append(word)
						else:
							head.children = []
				else:
					dataTree.append(word)
			
		# start here 
		for verb in dataTree['children']:					
			# get the verb
			if verb.relation == "PRED" or verb.relation == "PRED_CO":						
				#s, r, u, i, f, z, g, a = [], [], [], [], [], [], [], []
				u, i = [], []
				aim_words = []
				# group the words and make sure, save the selected words
				for word in verb.children:
											
					if word.relation == "COORD":
						u.append(word.tbwid)
						#aim_words.append(word)
						for w in word.children:
							#if w.head in u and (w.relation == "OBJ_CO" or w.relation == "ADV_CO") and w.pos != "participle" and w.pos != "verb":
							if (w.relation == "OBJ_CO" or w.relation == "ADV_CO") and w.pos != "participle" and w.pos != "verb":
								i.append(w.tbwid)
								aim_words.append(w)
					
					elif word.relation == "AuxP":
						#f.append(word.tbwid)
						aim_words.append(word)
						for w in word.children:
							#if w.head in f and w.relation != "AuxC" and w.pos != "participle":
							if w.relation != "AuxC" and w.pos != "participle":
								#z.append(w.tbwid)
								aim_words.append(w)
					
								for w2 in w.children:
									#if w2.head in z and w2.relation == "ATR" and w2.pos != "verb":
									if w2.relation == "ATR" and w2.pos != "verb":
										#a.append(w2.id)
										aim_words.append(w2)
										
										
					elif word.relation != "AuxC" and word.relation != "COORD" and word.pos != "participle":
						#r.append(word.tbwid)
						aim_words.append(word)
						for w in word.children:
							#if w.head in r and w.relation == "ATR" and w.pos != "verb":
							if w.relation == "ATR" and w.pos != "verb":
								#g.append(w.tbwid)
								aim_words.append(w)
					
				# refinement of u
				for id in u:
					for id2 in i:
						w = self.words.get(tbwid = id2)
						if w.head is id:
							aim_words.append(w)   
							
				aim_words.append(verb)
				aim_words = set(aim_words)
					
				# check if not verbs only are returned
				if len(aim_words) > 1:		
					# consider params
					if len(params) > 0:
						# check if aim_words and parameter filtered intersect 
						if len(list(aim_words & set(self.words.filter(**params)))) > 0:					
							# set and order words
							return sorted(aim_words, key=lambda x: x.tbwid, reverse=False)			
					else:		
						# set and order words
						return sorted(aim_words, key=lambda x: x.tbwid, reverse=False)
			
						#fo.close()				
						
		return None 
	

	# best this would be created while writing the backend not on calling the method
	def __unicode__(self):
		#words = ""
		#for obj in reversed(self.words.all()):
			#words+= obj.value + " "
		#return str(unicode(words)) or u''
		return unicode(self.sentence) or u''

class Slide(models.NodeModel):
	# Template refers to a front-end template
	# These are used to ultimately render the slide
	title = models.StringProperty()
	template = models.URLProperty()
=======
		return self.name
>>>>>>> restruct

class Unit(models.Model):
	textbook = models.ForeignKey('TextBook')
	name = models.CharField(max_length=200)
	color = models.CharField(max_length=7)
	graphic = models.FileField(upload_to='units')

	def __unicode__(self):
		return self.name


<<<<<<< HEAD
	# the actual user answer
	response = models.StringProperty()
	# also contains some of Giuseppes mappings to morph specifiactions
	task = models.StringProperty()
	smyth = models.StringProperty()
	# Set by the client, allows us to determine how must time the user spent
	# on a particular slide.
	time = models.IntegerProperty()
	# Set by the client. Scale from 1-100 of accuracy. Necessary for exercises that aren't strictly binary questions.
	accuracy = models.IntegerProperty()
	
	# maybe an array of CTS references?! URL array?!
	encounteredWords = models.ArrayProperty()
	# static or dynamic (direct_select, multi_comp, tree) 
	slideType = models.StringProperty()
	
	timestamp = models.DateTimeProperty()
	#finished = models.DateTimeProperty()

	user = models.Relationship(AppUser,
		rel_type='answered_by',
		single=True,
		related_name='submissions'
	)

	#slide = models.Relationship(Slide,
	#	rel_type='response_to',
	#	single=True,
	#	related_name='submissions'
	#)

	class Meta:
		app_label = 'models'

	def __unicode__(self):
		return unicode(self.response) or u''	
=======
class Lesson(models.Model):
	unit = models.ForeignKey('Unit')
	name = models.CharField(max_length=200)
>>>>>>> restruct

	def __unicode__(self):
		return self.name


class Slide(models.Model):
	lesson = models.ForeignKey('Lesson')
	name = models.CharField(max_length=200)
	content = models.TextField()
	smyth = models.CharField(max_length=10)
	tasks = models.CharField(max_length=200)

	def __unicode__(self):
		return self.name

