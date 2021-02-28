import builder
import os
import urllib
from markdown2 import markdown
import sql_tables
import re
import server
import json
import database_operations
import query_helper

message_404 = "404"


def get_frame():
	return open('frame.html').read()

def get_sidebar():
	list = sql_tables.get_names()
	result = "<ul>{}</ul>".format("".join(['<li><a href="{}">{}</a></li>'.format("/search/" + x + "?name:", x.capitalize()) for x in list]))
	quick = json.load(open('config/quick_links.json'))
	result += "<ul>{}</ul>".format("".join(['<li><a href="{}">{}</a></li>'.format(quick[x], x) for x in quick]))
	return result

def search(path):
	
	path = urllib.parse.unquote(path)
	type, query = path.split("?")
	
	raw = open("in").read().format(type, query)
	
	insert_button = '<div class="new_entry container" id="container_{0}_null"><button class="new_button" onclick="insertEditor(null, \'{0}\')">New</button></div>'.format(type)
	
	f = {}
	f['body'] = insert_button + "\n" + builder.parse(markdown(raw, extras=["tables"]), True)
	f['side-bar'] = get_sidebar()
	
	
	data = get_frame().format(**f)
	
	if path == "":
		return 404, message_404
	
	return 200, data.encode()

class Editor():
		
	def handle(self, url):
		_, _, mode, query, _ = urllib.parse.urlsplit(url)
		
		query = urllib.parse.parse_qs(query)
		query = {q: urllib.parse.unquote(query[q][0]) for q in query}
				
		data = {} if query['ID'] == 'null' else query_helper.get_entry(query['type'], query['ID'])
		columns = query_helper.get_columns(query['type'])
				
		print(data)
		result = ""
		
		#Hide ID field
		result += '<div class="InputContainer ID"><input name="ID" type="hidden" class="input_content" value="{}"></div>'.format(data.pop('ID', ''))
		#Remove DELETED field
		if 'DELETED' in data: data.pop('DELETED')
		
		for key in columns:
			content = str(data[key]) if key in data and data[key] else ''
			collapsed = 'false' if content != '' or key == 'content' else 'true'
			#if key in ['skill', 'leveling']:
			#	pass
			if key in ['name', 'requires_raw']:
				result += '<div class="InputContainer {0}" collapsed="{2}"><span class="input_label uncollapsable" onclick="toggle_collapse(this.parentElement);">{0}</span><input name="{0}" value="{1}" class="input_content"></div>'.format(str(key), content, collapsed)
			else:
				result += '<div class="InputContainer {0} collapsable" collapsed="{2}"><span class="input_label uncollapsable" onclick="toggle_collapse(this.parentElement);">{0}</span><textarea name="{0}" class="input_content">{1}</textarea></div>'.format(str(key), content, collapsed)
	
		
		result += '\n\n<button onclick="save(\'{}\',\'{}\',true,false)">Save</button>'.format(query['ID'], query['type'])
	
		result = '<div id="editor_{}_{}">{}</div>'.format(query['type'], query['ID'], result)
			
		return 200, result.encode()


def get_args(query):
	query = urllib.parse.parse_qs(query)
	query = {q: urllib.parse.unquote(query[q][0]) for q in query}
	return query
		
def get_fields_and_values(table, query):
	# Read the template to know all non ID columns
	template = open('templates/' + table).read()
	fields = [x.split(' ')[0] for x in template.split('\n') if x.startswith('`')]
	
	# Fetch values from the message
	values = ["'" + query[x[1:-1]] + "'" if x in query else "NULL" for x in fields]
	
	return fields, values

class ADD():
	def handle(self, url):
		_, _, mode, query, _ = urllib.parse.urlsplit(url)
		return _add(mode, query)
		
class UPDATE():
	def handle(self, url):
		_, _, table, query, _ = urllib.parse.urlsplit(url)
		query = get_args(query)
		
		
		#Get Data and fields
		fields, values = get_cols_and_values(table, query)
		
		#Build SQL statement
		sql = "UPDATE {} SET ({}) VALUES ({}) WHERE `ID` = ?".format(table, ",".join(fields), ",".join(['?' for i in range(len(col))]))
		
		try:
			con.cursor().execute(sql, val + [query["ID"]])
			con.commit()
			return 200, "Updated {} Succesfully".format(query['ID']).encode()
		except e:
			print(e)
			return 500, "Failed to update {}: {}".format(query['ID'] if 'ID' in query else "???", str(e)).encode()
		
		
class Search():
		
	def handle(self, url):
		return search(url)

class Get():
	def handle(self, url):
		_, _, table, query, _ = urllib.parse.urlsplit(url)
		query = get_args(query)
		try:
			data = query_helper.get_entry(table, query['ID'], include_deleted=query.get('include_deleted', False))
			return 200, json.dumps(data).encode(), {'Content-type': 'text/json'}
		except query_helper.EntryNotFound:
			return 404, 'Entry with ID {} not found, include the parameter "include_deleted=true" to include deleted results as well'.format(query['ID']).encode()
		
		

class Resource:
	def handle(self, raw_path):
		path = "resc/generated/" + raw_path
		if not os.path.isfile(path):
			path = "resc/static/" + raw_path
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
		
		return code, data, {'Content-type': mime}


class API(server.PatternHandler):
	def __init__(self):
		super().__init__()
		self.add_pattern('/add/', database_operations.ADD(query_helper.cons))
		self.add_pattern('/update/', database_operations.UPDATE(query_helper.cons))
		self.add_pattern('/delete/', database_operations.DELETE(query_helper.cons))
		self.add_pattern('/restore/', database_operations.RESTORE(query_helper.cons))
		self.add_pattern('/editor', Editor())
		self.add_pattern('/get/', Get())
		
		self.init()
