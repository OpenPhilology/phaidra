import markdown

DEL_RE = r'(--)(.*?)--'

class MyExtension(markdown.Extension):
	def extendMarkdown(self, md, md_globals):
		del_tag = markdown.inlinepatterns.SimpleTagPattern(DEL_RE, 'del')
		md.inlinePatterns.add('del', del_tag, '>not_strong')

def makeExtension(configs={}):
	return MyExtension(configs=configs)
