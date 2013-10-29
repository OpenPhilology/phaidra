from neo4django.db import models

class Document(models.NodeModel):
	CTS = models.StringProperty(max_length=200)	
	author = models.StringProperty(max_length=200)
	name = models.StringProperty(max_length=200)
	lang = models.StringProperty(max_length = 30)

