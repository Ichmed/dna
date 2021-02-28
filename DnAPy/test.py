from markdown2 import markdown
from shlex import split
import sqlite3
from http.server import *
from functools import lru_cache
import re

import sys, os
import urllib

widgets = {}

def link(type, target, text=None):
	if not text: 
		text = target
	
	exists = False
	try:
		c = con.cursor()
		c.execute("SELECT * FROM `{}` WHERE name=? LIMIT 1".format(type), [target])
		
		for row in c:
			data = {c.description[i][0]: row[i] for i in range(len(row)) if not row[i] == None}
			if 'content_short' in data:
				popup_text = data['content_short']
			else: popup_text = "..."
			
			exists = True
			break
	except Exception as e:
		pass
	
	if exists:
		return {"link": '<span class="smartlink tooltip" onClick="smartlink(\'{}\', \'{}\');">{}<span class="tooltiptext">{}</span></span>'.format(type, target, text, popup_text)}, []
	else :
		return {"link": '<span class="brokenLink">{}</span>'.format(text)}, []

widgets['link'] = link

def perform_query(type, query, con):
	c = con.cursor()
	WHERE = []
	
	if type == 'abilities':
		ORDER = "`root`, `index`"
		#ORDER = "`skill`"
	elif type == 'rules':
		ORDER = "`priority`, `name`"
	else:
		ORDER = "`name`"
		
	fields = []
	values = []
		
	for q in query.split("+"):
		if "=" in q:
			WHERE += ["{}=?"]
			fields += [q.split("=")[0]]
			values += [q.split("=")[1]]
		elif ":" in q:
			WHERE += ["{} LIKE ?"]
			fields += [q.split(":")[0]]
			values += ['%{}%'.format(q.split(":")[1])]
		
	WHERE = " AND ".join(WHERE)
	
	q = "SELECT * FROM `{}` WHERE {} ORDER BY {}".format(type, WHERE, ORDER).format(*fields)
	#print(q)
	try:
		c.execute(q, values)
	except:
		return None
	
	return c

def container(type, query, show_result_count=False):
	
	for con in cons:
		c = perform_query(type, query, con)
		
		if not c:
			return {'error' :"[ERROR] {} {}".format(type, query)}, []
		
		result = {}
		result_list = []
		count = 0
		
		all_data = {}
		
		for row in c:
			data = {c.description[i][0]: row[i] for i in range(len(row)) if not row[i] == None}
			#print(data['name'])
			if 'parent' in data: all_data[data['name'] + data['parent']] = data
			else: all_data[data['name']] = data
		
	for row in all_data:
		data = all_data[row]
		
		if 'parent' in data and data['parent'] in all_data: 
			#print('skipping', data['name'], 'parent', data['parent'], 'already present')
			continue
		
		editor_button = '<button onclick="insertEditor(\'{}\', \'{}\', \'{}\')">Edit</button>'.format(data['name'], data['parent'] if 'parent' in data else '', type)
		#print(data)
		
		
		#data ={'name': 'Ignite', 'other': test}
		inner = '<div style="cursor: pointer;" onclick="toggle_collapse(this.parentElement);" class="container_data_name uncollapsable"><h1>{}</h1></div>'.format(str(data['name']))
		name = data['name']
		parent = data['parent'] if 'parent' in data else ''
		data.pop('name')
		
		left = ""
		right = ""
		
		for key in data:
			if type == 'abilities':
				if key in ['root', 'parent', 'index', 'tags', 'skill', 'leveling', 'requires_raw']: continue
				elif key == 'cost':
					skill_cost = ''.join(['<img src="/resc/symbols/bobble{}.png">'.format(data.get('skill')) for i in range(int(data['cost']))])
					
					if 'leveling' in data:
						if data['leveling'] != 'None':
							skill_cost += '<img src="/resc/symbols/upgrade{}.png">'.format(data['leveling'])

					inner += '<div class="uncollapsable skill_cost">{}</div>'.format(skill_cost)
							
				elif key == 'manacost':
					try:
						manacost = int(data['manacost'])
					except:
						manacost = 0
					
					manacost_symbols = ""
					
					if manacost == 1:
						manacost_symbols += '<img src="/resc/symbols/iconManaSingle.png">'
					elif manacost > 1:
						if manacost > 10:
							manacost_symbols += '{}x<img src="/resc/symbols/iconManaSingle.png">'.format(manacost)
						else:
							manacost_symbols += '<img src="/resc/symbols/iconManaLeft.png">'
							manacost_symbols += ''.join(['<img src="/resc/symbols/iconMana.png">' for i in range(1, manacost - 1)])
							manacost_symbols += '<img src="/resc/symbols/iconManaRight.png">'
							manacost_symbols += "<span>({})</span>".format(manacost)
					right += '<div><div>{}</div><div>{}</div></div>'.format(markdown(parse("**Manacost**: " + data['manacost']), extras=["tables"]), manacost_symbols)
				else:
					res = markdown(parse("**" + str(key).capitalize() + "**: " + str(data[key])), extras=["tables"])
					if key in ['effect', 'result', 'flavor']:
						left += '<div class="container_data_{}">{}</div>'.format(key, res)
					else:
						right += '<div class="container_data_{}">{}</div>'.format(key, res)

			elif type == 'rules':
				if key == 'content':
					s = parse(markdown(str(data[key]), extras=["tables"]))
					inner += '<div  class="container_data_{}" style="clear: none;">{}</div>'.format(key, s)
			
			elif type == 'races':
				if key == 'str':
					atts = [["CON", "DEX", "INT", "WIL", "INS"], ["STR", "FIN", "ING", "DEV", "CHA"], ["FRT", "AGI", "REC", "COU", "CRE"]]
					
					tbl = "<table>{}</table>"
					tr = "<tr>{}</tr>"
					td = '<td><div>{}</div><div>{}</div></td>'
					
					inner += tbl.format("\n".join([tr.format("".join([td.format(att, data[att.lower()] if att.lower() in data else " ") for att in list])) for list in atts]))
				
			else:
				s = parse(markdown(str(data[key]), extras=["tables"]))
				inner += '<div  class="container_data_{}" style="clear: none;">{}</div>'.format(key, s)
		
		inner += '<table style="width: 100%;"><tr style="vertical-align: top;"><td style="text-align: left; width: 80%; padding-right: 10%;">\n{}\n<td style="text-align: left; width: 20%;">\n{}\n</tr></table>'.format(left, right)
		#inner += "\n{}\n\n{}\n".format(left, right)
		
		inner += editor_button
		
		if type in ['abilities', 'rules']:
			containers, names = container(type, "parent={}".format(name))
			inner += "\n".join(list(containers.values()))
			result_list += names
		
		if type == 'abilities':
			if parent == '' and 'root' in data: inner += tree(data['root'])[0]['tree']
			pass
		frame = '<div class="container_wrapper"><div collapsed=true class="collapsable data_container {}_container" id="container_{}_{}">{}</div></div>'
		#if type == "rules":
		#	result[name + "_" + parent] = frame.format(type, name, "", inner)
		#else:
		result[name + "_" + parent] = frame.format(type, name, parent, inner)
		
		count += 1
		
	#if show_result_count:
	#	result = "<p><span class=result_amount_text><span class=result_amount>{}</span> results found</span></p>".format(count) + result
	
	for key in result_list: result.pop(key, None)
	
	result_list += result.keys()
	
	return result, set(result_list)
	
widgets['container'] = container
widgets['c'] = container
widgets['C'] = container

def table(type, query, title=None, limit=None, wide="True", include_links=True):
	c = perform_query(type, query)
	
	if not c:
		return {'error' :"[ERROR] {} {}".format(type, query)}, []
		
	if limit: limit = [s.strip() for s in limit.split(",")]
	
	header = '<tr>{}</tr>'.format("".join(['<th>{}</th>'.format(key[0].capitalize()) for key in c.description if not limit or key in limit]))
	
	td = '<td class="table_data_{}">{}</td>'
	data = []
	for r in c:
		row = []
		for i in range(len(r)):
			desc = c.description[i][0]
			if limit and desc in limit: continue
			
			if(r[i] == None): d = ""			
			elif desc == "name":
				d = link(type, r[i])[0]['link']
			else:
				d = r[i]
			row.append(td.format(desc, d))
		data.append('<tr>{}</tr>'.format("".join(row)))
		
	
	data = "\n".join(data)
	return {"table": '<div class="widget_table {}">{}<table>{}\n{}</table></div>'.format( "wide" if wide == "True" else "", '<h2>' + title + '</h2>' if title else "",header, data)}, []

widgets['table'] = table	

def calc_width(root, children, width={}):
	width = {}
	w = 0
	for c in children[root]:
		if c in width: continue
		width = {**width, **calc_width(c, children, width)}
		w += width[c]
	if w == 0: w = 1
	width[root] = w
	
	return width
	
@lru_cache(maxsize=None)
def tree(root, distance = 30, size = 20):
	# A list containing the parents for each node
	parents = {}
	cursor = con.cursor()
	done = []
	todo = [root]
	
	# A list containing the children for each node
	children = {}
	
	while len(todo) > 0:
		name = todo.pop()
		done += [name]
		cursor.execute("SELECT * FROM `ability_requirements` WHERE ability=?", [name])
		p = [x[1] for x in cursor]
		parents[name] = p
		
		cursor.execute("SELECT * FROM `ability_requirements` WHERE required=?", [name])
		c = [x[0] for x in cursor]
		children[name] = c
		
		todo = [x for x in set(list(todo) + p + c) if x not in done]
	
	width = calc_width(root, children)
	coords = {}
	
	for node in done:
		c_width = min(1, sum([width[x] if x in width else 1 for x in children[node]]))
		
		if not node in coords:
			coords[node] = [0, 0]
		pos = coords[node]
		x = pos[0] - (c_width - 1) / 2.0
		
		for parent in parents[node]:
			if not parent in coords:
				coords[parent] = [x, pos[1] + 1]
				x += width[parent] if parent in width else 1
			else:
				if coords[parent][1] < pos[1]:
					coords[parent][1] += 1
					#coords[parent][0] = x
					
		x = pos[0] - (c_width - 1) / 2.0
		
		for child in children[node]:
			if not child in coords:
				coords[child] = [x, pos[1] - 1]
				x += width[child] if child in width else 1
			else:
				if coords[child][1] > pos[1]:
					coords[child][1] -= 1
					#coords[child][0] = x
	
	min_y = 0
	max_y = 1
	min_x = 0
	max_x = 1
	for c in coords:
		c = coords[c]
		if c[0] < min_x: min_x = c[0]
		if c[0] > max_x: max_x = c[0]
		
		if c[1] < min_y: min_y = c[1]
		if c[1] > max_y: max_y = c[1]
	
	
	width = (max_x - min_x + 1) * distance
	height = (max_y - min_y) * distance
	
	lines = []
	
	for x in done:
		for p in parents[x]:
			pos = [(coords[x][0] - min_x) * distance + size/2, height - (coords[x][1] - min_y + 1) * distance, (coords[p][0] - min_x) * distance + size/2, height - (coords[p][1] - min_y + 1) * distance + size]
			lines.append("\n".join(['<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="black" />'.format(*pos) for p in parents[x]]))
	
	bobbles = []
	
	for x in coords:
		skill = cursor.execute("SELECT `skill` FROM `abilities` WHERE name=?", [x]).fetchone()
		if skill: skill = skill[0]
		else: continue
		pos = [x, x, skill, (coords[x][0] - min_x) * distance, height - (coords[x][1] - min_y + 1) * distance]
		
		bobbles.append('<img onclick="smartlink(\'abilities\', \'{}\')" class="skilltree_bobble" title="{}" src="/resc/symbols/bobble{}.png" style="position: absolute; left:{}; top:{}">'.format(*pos))
	
	bobbles = "\n".join(bobbles)
	
	lines = "\n".join(lines)
	
	return {'tree': '<div class="skilltree"><div><svg style="position: relative; height:{}; width:{};">{}</svg>\n{}</div></div>'.format(height, width, lines, bobbles)}, []

widgets['tree'] = tree

@lru_cache(maxsize=None)
def get_prime_elements():
	list = []
	c = con.cursor()
	c.execute("SELECT * FROM `potions` WHERE `parent` IS NULL")
	for e in c:
		list.append(e)
		
	c.close()
	return list

def create_widget(source, expand):
	type, *args = source
	
	if not type in widgets:
		return '[Unknown widget "{} {}"]'.format(type, args)
	
	if not expand:
		if widgets[type] == container:
			return widgets['link'](*args)
	return "\n".join(list(widgets[type](*args)[0].values()))

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
	

frame = """<html>
<head>
<link rel="stylesheet" type="text/css" href="/resc/main.css">
<script src="/resc/scripts/editorScript.js"></script>
<script src="/resc/scripts/smartLink.js"></script>
<script src="/resc/scripts/autosize.js"></script>
</head>
<body>
{}
</body></html>"""

class Handler(BaseHTTPRequestHandler):
	
	def do_GET(self):
		_, handler, *path = self.path.split("/")
		
		
		if not handler in handlers:
			path = [handler] + path
			handler = 'resc'
			
		code, data, mime = handlers[handler]("/".join(path))
		
		self.send_response(code)
		self.send_header('Content-type', mime)
		self.end_headers()
		self.wfile.write(data)
	
message_404 = "Error 404"

def resc(path):
	path = "resc/" + path
	if not os.path.isfile(path):
		mime = "text/html"
		code = 404
	elif path.endswith(".css"):
		code = 200
		mime = "text/css"
	elif path.endswith(".ico"):
		code = 200
		mime = "image/ico"
	elif path.endswith(".png"):
		code = 200
		mime = "image/png"
	elif path.endswith(".js"):
		code = 200
		mime = "text/js"
	else:
		mime = "text/html"
		code = 404
		
	if not mime.startswith('text'):
		data = open(path, 'rb').read() if code == 200 else message_404.encode()
	else:
		data = open(path).read().encode() if code == 200 else message_404.encode()
	
	return code, data, mime
	
def api(path):
	_, _, mode, query, _ = urllib.parse.urlsplit(path)
	
	query = urllib.parse.parse_qs(query)
	
	query = {q: urllib.parse.unquote(query[q][0]) for q in query}
	
	if mode == 'editor':
		condition = "name=?" if not 'parent' in query else "name=? and parent=?"
		fields = [query['name']] if not 'parent' in query else [query['name'], query['parent']]
		
		c = con.cursor()
		if(query['name'] == 'null'):
			c.execute("SELECT * FROM `{}` LIMIT 1".format(query['type']))
		else:
			c.execute("SELECT * FROM `{}` WHERE {}".format(query['type'], condition), fields)
		
		
		print(c)
		
		result = ""
		for row in c:
			if(query['name'] == 'null'):
				data = {c.description[i][0]: "" for i in range(len(row))}
			else:
				data = {c.description[i][0]: row[i] for i in range(len(row))}
			if not 'parent' in data or data['parent'] == None: data['parent'] = ''
			
			
			for key in data:
				content = str(data[key]) if data[key] else ''
				collapsed = 'false' if content != '' else 'true'
				#if key in ['skill', 'leveling']:
				#	pass
				if key in ['name', 'requires_raw']:
					result += '<div class="InputContainer {0} collapsable" collapsed="{2}"><span class="input_label uncollapsable" onclick="toggle_collapse(this.parentElement);">{0}</span><input name="{0}" value="{1}" class="input_content"></div>'.format(str(key), content, collapsed)
				else:
					result += '<div class="InputContainer {0} collapsable" collapsed="{2}"><span class="input_label uncollapsable" onclick="toggle_collapse(this.parentElement);">{0}</span><textarea name="{0}" class="input_content">{1}</textarea></div>'.format(str(key), content, collapsed)
		
			
			result += '\n\n<button onclick="save(\'{}\',\'{}\',\'{}\',true,false)">Save</button>'.format(data['name'], data['parent'], query['type'])
		
			result = '<div id="editor_{}_{}">{}</div>'.format(data['name'], data['parent'], result)
		
		print(result)
		
		return 200, result.encode(), 'text/html'
	elif mode.startswith('add'):
	
		if mode == 'add/abilities':
			if not 'parent' in query or query['parent'] == None:
				query['parent'] = ""
			root = query['name']
			if 'requires_raw' in query:
				req = query['requires_raw'].split(',')
				req_display = [re.sub(r'\(.*?\)', '', x) for x in req]
				req_true = [re.sub(r'§.*?§', '', x) for x in req]
				
				for i in range(len(req)):
					#print([query['name'], req_true[i], req_display[i]])
					con.cursor().execute("REPLACE INTO ´ability_requirements´ (ability, required, display) VALUES (?, ?, ?)", [query['name'], req_true[i], req_display[i]])
				
				if not 'root' in query or query['root'] == "":
					query['root'] = req_true[0]
				
				#print(query['requires_raw'])
			if not 'root' in query or query['root'] == "":
				query['root'] = query['name']
		
		
		col = ['`{}`'.format(key) for key in query if len(query[key]) or key == 'parent']
		val = ["{}".format(query[key]) for key in query if len(query[key]) or key == 'parent']
		sql = "REPLACE INTO {} ({}) VALUES ({})".format(mode.split("/")[1], ", ".join(col), ", ".join(['?' for i in range(len(col))]))
		
		con.cursor().execute(sql, val)
		con.commit()
		
		return 200, 'OK'.encode(), 'text/html'
		
def search(path):
	
	path = urllib.parse.unquote(path)
	type, query = path.split("?")
	
	raw = open("in").read().format(type, query)
	
	insert_button = '<div class="new_entry" id="container_null_null"><button class="new_button" onclick="insertEditor(null, null, \'{}\')">New</button></div>'.format(type)
	
	data = frame.format(insert_button + "\n" + parse(markdown(raw, extras=["tables"]), True))
	
	if path == "":
		return 404, message_404, "text/html"
	
	return 200, data.encode(), "text/html"

	
handlers = {}
handlers['api'] = api
handlers['search'] = search
handlers['resc'] = resc

if __name__ == "__main__":
	con = sqlite3.connect('dna.db')
	cons = [con]
	with HTTPServer(('', 8000), Handler) as server:
		server.serve_forever()
