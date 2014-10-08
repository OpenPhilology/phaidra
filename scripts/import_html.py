# In progress: importing all our slide content into the database, stripped down to markdown.

import os, sys
base = os.path.dirname(os.path.dirname(__file__))
base_parent = os.path.dirname(base)
sys.path.append(base)
sys.path.append(base_parent)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phaidra.settings')

import django
django.setup()

import html2text
from app.models import Content, Grammar, Language

indir = '/opt/phaidra/static/content/en/slides/'
en_lang = Language.objects.get(name='English')
gr_lang = Language.objects.get(name='Ancient Greek')
ref = Grammar.objects.get(ref='s1')

for root, dirs, filenames in os.walk(indir):
	for files in filenames:
		with open(os.path.join(root, files), 'r') as f:
			text = f.read().decode('utf8')
			content = html2text.html2text(text)
			c = Content(title='UPDATE ME!', content=content, grammar_ref=ref, source_lang=en_lang, target_lang=gr_lang)
			c.save()
