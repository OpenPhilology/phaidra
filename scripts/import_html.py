# In progress: importing all our slide content into the database, stripped down to markdown.

import os
import html2text

indir = '/opt/phaidra/static/content/en/slides/4.cases'

for root, dirs, filenames in os.walk(indir):
	for files in filenames:
		with open(os.path.join(root, files), 'r') as f:
			text = f.read().decode('utf8')
			print(html2text.html2text(text))
