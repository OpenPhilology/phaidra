import markdown
from markdown.inlinepatterns import Pattern

# PREMISE_RE = r'(\[p )(.*?)\]'
TIP_RE = r'(\[tip\])(.*?)\[\/tip]'

class AttrTagPattern(Pattern):
	def __init__(self, pattern, tag, attrs):
		Pattern.__init__(self, pattern)
		self.tag = tag
		self.attrs = attrs

	def handleMatch(self, m):
		el = markdown.util.etree.Element(self.tag)
		el.text = m.group(3)
		for (key, val) in self.attrs.items():
			el.set(key, val)
		return el

class TipExtension(markdown.Extension):
	def extendMarkdown(self, md, md_globals):
		tip_tag = AttrTagPattern(TIP_RE, 'span', {'class': 'tip'})
		md.inlinePatterns.add('tip', tip_tag, '_begin')

def makeExtension(configs={}):
	return TipExtension(configs=configs)
