from django.core.management.commands.dumpdata import Command

class Command(Command):
    def handle(self, *args, **options):
        options['--natural'] = options.get('--natural') 

        super(Command, self).handle(*args, **kwargs)
