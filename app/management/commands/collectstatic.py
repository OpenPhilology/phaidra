from django.contrib.staticfiles.management.commands.collectstatic import Command
from django.conf import settings

class Command(Command):
	def set_options(self, **options):
		super(Command, self).set_options(**options)
		self.ignore_patterns += settings.COLLECT_STATIC_IGNORE
		self.ignore_patterns = list(set(self.ignore_patterns))
