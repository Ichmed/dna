import markdown2
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.template import loader
from traceback import print_exc

from rulebook.query import perform_query, get_model_for_name
from django.db.models import BooleanField, ManyToOneRel, ManyToManyField, ManyToManyRel

register = template.Library()

@register.filter
def cat(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)


widgets = {}

def get_widget(name):
	return widgets[name]

def load_widget(name, libname=None, abs=[]):
	"""
	Load a widget from a python file
	"""
	if not libname: libname = "rulebook.widgets." + name
	# print("loading", name, "from", libname)
	for n in [name] + abs:
		widgets[n] = getattr(getattr(__import__(libname), 'widgets'), name).build

def create_search_widget(name, path, *args_names, alts=[]):
	@mark_safe
	def func(table, query, *args):
	
		m = get_model_for_name(table)
		display = None
		if not "=" in query and not ":" in query:
			display = query
			query = "name=" + query

		result = perform_query(table, query)

		results_as_dicts = []

		for e in result:
			c = {}
			for x in m._meta.get_fields(include_hidden=False):
				if x.name == "DELETED": continue
				if type(x) == ManyToOneRel: 
					continue
				#Construct the displayed requires_raw field from the actual requires_raw field and the abilities that are stored as MtM
				#print(x.name)
				if x.name == 'parent' and e.parent:
					c['parent_id'] = e.parent.id
					continue
				elif x.name == 'id' and e.id:
					c['self_id'] = e.id
					continue
				elif x.name == 'requires_raw':
					r = []
					for parent in e.requirement.all():
						if parent.requires.name == parent.display:
							r.append(parent.display)
						else:
							r.append(parent.requires.name + "|" + parent.display)
					if e.requires_raw != None: r += e.requires_raw.split('\n')
					e.requires_raw = ";".join(r)
				else:
					c[x.name] = getattr(e, x.name) or ""

			results_as_dicts.append(c)
					
					
	

		context = {"results": result, "results_as_dicts": results_as_dicts, "type": table, "query": query}
		if display: context['display'] = display
		context.update({args_names[i]: args[i] for i in range(len(args))})
		return loader.get_template("rulebook/" + path + ".html").render(context)
		
	widgets[name] = func
	for n in alts:
		widgets[n] = func

def add_html_widget(name, path=None, abs=[]):
	"""
	Register a widget that is just the contents of an html file
	"""
	if path == None:
		path = "rulebook/static/rulebook/widgets/" + name + ".html"
		
	def func():
		return open(path).read()
	
	for n in [name] + abs:
		widgets[n] = func
	
create_search_widget('link', 'widgets/link', 'display')
create_search_widget('container', 'search_inner', alts=['c'])
create_search_widget('table', 'table', 'cols', alts=['t'])

# load_widget('container', abs=['c'])
# load_widget('table')
load_widget('crafting')
# load_widget('quickbox')
# load_widget('tree', 'widgets.tree_2')
add_html_widget('armor_calc')
# load_widget('wiki')

from .cache import push, pop, get, put
from shlex import split
from django.template.loader import render_to_string

@register.filter
def container_from_data(data, t):
	key = "['container', '{}', 'id={}']".format(t, data.id)
	result = get(key)
	push(key)
	if result:
		put()
	else:
		#print('Missed "' + key + '" in cache')
		result = render_to_string("rulebook/" + t + ".html", {"data": data, "type": t, "skip": False})
		put(result + "")
		push("data:{}:{}".format(t, data.id))
		put()
		pop()
	pop()
	return mark_safe(result)

@register.filter
@stringfilter
def widget(source):
	return create_widget(split(source))

@mark_safe
def create_widget(source):
	key = str(source)
	result = get(key)
	push(key)
	
	if result:
		#print('Hit "' + key + '" in cache')
		put()
	else:
		#print('Missed "' + key + '" in cache')

		type, *args = source
		
		if not type in widgets:
			pop()
			return '[Unknown widget "{} {}"]'.format(type, args)
		
		try:
			w = widgets[type](*args)
			result = w.replace("\n", "").replace("\r", "")
		except Exception as e:
			print_exc()
			result = '<div class="widget error">Failed to build widget "{}: {} {}"</div>'.format(e, type, args)
		put(result)

		#print(result)
	
	pop()
	return result

@register.filter
@stringfilter
@mark_safe
def md(value):
	return markdown2.markdown(value, extras=["tables"])


from .parse import parse as p
@register.filter
@stringfilter
def parse(text, skip=True):
	if skip: return text
	else: return md(p(text))

@register.filter
@stringfilter
def trim(value):
    return value.strip()