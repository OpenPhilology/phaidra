from neo4django.db import models

class Slide(models.NodeModel):
	# Template refers to a front-end template
	# These are used to ultimately render the slide
	title = models.StringProperty()
	template = models.URLProperty()

	# Options is an array of possible solutions to this slide.
	# It is only applicable to slides that require feedback
	options = models.ArrayProperty()

	# Used to compare user-submitted answers to acceptable answers
	answers = models.ArrayProperty()

	# Corresponds to the type of slide that will be created for this slide
	# See the possible options in `static/js/views`, js files prefixed with slide_.
	view = models.StringProperty()

	# Determines the type of comparisons the system makes between
	# user-submitted answers and accepted answers
	require_all_answers = models.BooleanProperty()
	require_order = models.BooleanProperty()
