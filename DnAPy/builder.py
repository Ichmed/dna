from shlex import split
from traceback import print_exc

widgets = {}

def parse(text, expand=True):
	result = ""
	widget = None
	parenthesis = 0
	i = 0
	while i < len(text):
		if parenthesis == 0 and text[i] == "$":
			#i += 1
			if text[i + 1] == '$':
				result += '$'
				i += 2
				continue
			widget = text[i]
		elif widget != None:
			widget += text[i]
			if text[i] == "(":
				parenthesis += 1
			elif text[i] == ")":
				parenthesis -= 1
				
			if parenthesis == 0:
				result += create_widget(split(widget[2:-1]), expand)
				widget = None
				
		else:
			result += text[i]
		#print(result)
		i += 1

	return result

def get_widget(name):
	return widgets[name]

def load_widget(name, libname=None, abs=[]):
	"""
	Load a widget from a python file
	"""
	if not libname: libname = "widgets." + name
	print("loading", name, "from", libname)
	for n in [name] + abs:
		widgets[n] = getattr(__import__(libname), libname.split('.')[-1]).build

def add_html_widget(name, path=None, abs=[]):
	"""
	Register a widget that is just the contents of an html file
	"""
	if path == None:
		path = "resc/static/" + name + ".html"
		
	def func():
		return {name: open(path).read()}, []
	
	for n in [name] + abs:
		widgets[n] = func
	
load_widget('link')
load_widget('container', abs=['c'])
load_widget('table')
load_widget('crafting')
load_widget('quickbox')
load_widget('tree', 'widgets.tree_2')
add_html_widget('armor_calc')
load_widget('wiki')

def create_widget(source, expand):
	type, *args = source
	
	if not type in widgets:
		return '[Unknown widget "{} {}"]'.format(type, args)
	
	try:
		if not expand:
			if widgets[type] == container:
				return widgets['link'](*args)
		return "\n".join(list(widgets[type](*args)[0].values()))
	except Exception as e:
		print_exc()
		return '<div class="widget error">Failed to build widget "{} {}"</div>'.format(type, args)