import urllib, re, widgets.tree
from time import time
from traceback import print_exc
import query_helper

def get_args(query):
	query = urllib.parse.parse_qs(query)
	query = {q: urllib.parse.unquote(query[q][0]) for q in query}
	return query
		
def get_cols_and_values(table, query):
	# Read the template to know all non ID columns
	template = open('data/templates/' + table).read()
	fields = [x.split(' ')[0] for x in template.split('\n') if x.startswith('`')]
	
	# Fetch values from the message
	values = [query[x[1:-1]] if x[1:-1] in query else None for x in fields]
	
	return fields, values


handlers = {}
def on(function, time='after', action='__all__', table='__all__'):
	handlers.setdefault(action, {})
	handlers[action].setdefault(time, {})
	handlers[action][time].setdefault(table, [])
	h = handlers[action][time][table]
	print(handlers)
	h.append(function)
	handlers[action][time][table] = h
	
	
def get_callbacks(time, action, table):
	result = []
	for a in [action, '__all__']:
		for b in [table, '__all__']:
			result += handlers.get(a, {}).get(time, {}).get(b, [])
	return result
	
def update_ability_requirements(query, table, con):
	if 'requires_raw' in query:
		
		#split requirement
		req = query['requires_raw'].split(',')
		req_display = [re.sub(r'\(.*?\)', '', x) for x in req]
		req_true = ["'" + re.sub(r'§.*?§', '', x) + "'" for x in req]
		
		#get ids for requireds
		cursor = con.cursor()
		cursor.execute("SELECT ID FROM `abilities` WHERE `name` IN ({})".format(','.join(req_true)))
		ids = [x[0] for x in cursor]
		args = zip([query['ID'] for i in req], ids, req_display)
		
		#print(list(args))
		cursor.executemany("REPLACE INTO `ability_requirements` VALUES (?, ?, ?)", args)
		
		
		if not 'root' in query or query['root'] == "":
			root = query['ID']
			
			for id in ids:
				d = cursor.execute('SELECT `root` FROM `abilities` WHERE id = ?', [id]).fetchone()
				if not d: continue
				if d[0] == None: continue
				root = d[0]
				break
			
			#update roots
			query['root'] = root
		
		#print(query['requires_raw'])
	else:
		if not 'root' in query or query['root'] == "":
			query['root'] = query['ID']

	print(query['root'])
	return query

class ADD():
	def __init__(self, cons):
		self.cons = cons
		
	def handle(self, url):
		con = self.cons[-1]
		_, _, table, query, _ = urllib.parse.urlsplit(url)
		query = get_args(query)
				
		for f in get_callbacks('before', 'ADD', table):
			f(query, table, con)
		
		#Get Data and fields
		cols, values = get_cols_and_values(table, query)
		
		if 'parent' in query:
			try:
				int(query['parent'])
			except:
				query['parent'] = query_helper.get_id_for_name(table, query['parent'])
		
		#Build SQL statement
		sql = "INSERT INTO {} ({}) VALUES ({})".format(table, ",".join(cols), ",".join(['?' for i in range(len(cols))]))
		
		
		try:
			con.cursor().execute(sql, values)
			con.commit()
			for f in get_callbacks('after', 'ADD', table):
				query = f(query, table, con)
			return 200, "Added {} Succesfully".format(query.get('ID', 'New Ability')).encode()
		except Exception as e:
			print_exc()
			return 500, "Failed to add {}: {}".format(query['ID'] if 'ID' in query else "???", str(e)).encode()

class UPDATE():
	def __init__(self, cons):
		self.cons = cons
		
	def handle(self, url):
		con = self.cons[-1]
		_, _, table, query, _ = urllib.parse.urlsplit(url)
		query = get_args(query)
		
		
		for f in get_callbacks('before', 'UPDATE', table):
			query = f(query, table, con)
			
		#Get Data and fields
		cols, values = get_cols_and_values(table, query)
		
		#Build SQL statement
		sql = "UPDATE {} SET {} WHERE `ID` = ?".format(table, ",".join([c + '=?' for c in cols]))
				
		try:
			con.cursor().execute(sql, values + [query["ID"]])
			con.commit()
			for f in get_callbacks('after', 'UPDATE', table):
				print(f)
				f(query, table, con)
			return 200, "Updated {} Succesfully".format(query.get('ID', 'New Ability')).encode()
		except Exception as e:
			print_exc()
			return 500, "Failed to update {}: {}".format(query['ID'] if 'ID' in query else "???", str(e)).encode()

class DELETE():
	def __init__(self, cons):
		self.cons = cons
		
	def handle(self, url):
		con = self.cons[-1]
		_, _, table, query, _ = urllib.parse.urlsplit(url)
		query = get_args(query)
		
		
		for f in get_callbacks('before', 'DELETE', table):
			query = f(query, table, con)
		
		#Build SQL statement
		sql = "UPDATE {} SET DELETED = ? WHERE `ID` = ?".format(table)
				
		try:
			con.cursor().execute(sql, [int(time()), query["ID"]])
			con.commit()
			for f in get_callbacks('after', 'DELETE', table):				
				f(query, table, con)
			return 200, "Deleted {} Succesfully".format(query.get('ID', 'New Ability')).encode()
		except Exception as e:
			print_exc()
			return 500, "Failed to delete {}: {}".format(query['ID'] if 'ID' in query else "???", str(e)).encode()
			
class RESTORE():
	def __init__(self, cons):
		self.cons = cons
		
	def handle(self, url):
		con = self.cons[-1]
		_, _, table, query, _ = urllib.parse.urlsplit(url)
		query = get_args(query)
		
		
		for f in get_callbacks('before', 'DELETE', table):
			query = f(query, table, con)
		
		#Build SQL statement
		sql = "UPDATE {} SET DELETED = NULL WHERE `ID` = ?".format(table)
				
		try:
			con.cursor().execute(sql, [query["ID"]])
			con.commit()
			for f in get_callbacks('after', 'DELETE', table):				
				f(query, table, con)
			return 200, "Restored {} Succesfully".format(query.get('ID', 'New Ability')).encode()
		except Exception as e:
			print_exc()
			return 500, "Failed to restore {}: {}".format(query['ID'] if 'ID' in query else "???", str(e)).encode()


def parent_to_id(query, table, con):
	if not 'parent' in query: return query
	
	try:
		int(query['parent'])
	except:
		query['parent'] = query_helper.get_id_for_name(table, query['parent'])
	
	return query

on(parent_to_id, 'before', '__all__')
#on(update_ability_requirements, 'before', '__all__', 'abilities')
on(lambda x, y, z: widgets.tree.cache.clear(), 'after', '__all__', 'abilities')
