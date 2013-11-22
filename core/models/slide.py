from neo4django.db import models

class Slide(models.NodeModel):
	# Template refers to a front-end template
	# These are used to ultimately render the slide
	title = models.StringProperty()
	template = models.URLProperty()

	# Either a template or an exercize side_type is provided, not both.
	# Exercises are interactive, whereas templates are information only.
	exercise = models.StringProperty()

	# Options is an array of possible solutions to this slide.
	# It is only applicable to slides that require feedback
	options = models.ArrayProperty()

	# Used to compare user-submitted answers to acceptable answers
	answers = models.ArrayProperty()

	# Determines the type of comparisons the system makes between
	# user-submitted answers and accepted answers
	require_all_answers = models.BooleanProperty()
	require_order = models.BooleanProperty()

	def __unicode__(self):
		return str(self.pk)

