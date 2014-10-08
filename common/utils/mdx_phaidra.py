from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension

# class LanguageParser(Treeprocessor):
# 	def __init__(self, md):
# 		super(LanguageParser, self).__init__(md)
# 	def run(self, root):
# 		return self.setClass(root)
# 	def setClass(self, element):
# 		for child in element:
# 			if child.tag == 'code':
# 				content = child.text
# 				langClass = re.match('^ *language-\w+', content)
# 				if langClass is not None:
# 					strippedContent = re.sub('^ *language-.*\n', '', content)
# 					child.set('class', langClass.group(0))
# 					child.text = strippedContent
# 			child = self.setClass(child)
# 		return element

class LanguageParserExtension(Extension):
	def extendMarkdown(self, md, md_globals):
		md.treeprocessors.add('languageparser', LanguageParser(md), '_end')
