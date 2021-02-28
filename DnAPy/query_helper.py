import json, os, sqlite3
from functools import lru_cache
import main

class NoDatabasesConnected(Exception):
	pass
	
class EntryNotFound(Exception):
	pass

def create_db(name):
	db = sqlite3.connect('data/' + name + '.db')
	cursor = db.cursor()
	for spec_file in os.listdir('data/templates'):
		if not os.path.isfile('data/templates/' + spec_file): continue
		spec = "{}(\nID INTEGER PRIMARY KEY AUTOINCREMENT,\nDELETED INTEGER DEFAUL NULL,\n{}\n)".format(spec_file, open('data/templates/' + spec_file).read())
		cursor.execute("CREATE TABLE IF NOT EXISTS " + spec)
		cursor.execute("CREATE INDEX IF NOT EXISTS " + spec_file + "_deleted ON " + spec_file + " (DELETED)")
	
	for spec_file in os.listdir('data/templates/non_standard'):
		cursor.execute(open('data/templates/non_standard/' + spec_file).read())
		
	return db

cons = []

db = open('data/db').read()

for name in db.split('\n'):
	if name.startswith('#') or name == "":
		continue
	if not os.path.isfile('data/' + name + '.db'):
		print(name, 'is not an existing database, would you like to create it (y/[n]))')
		if not input() == 'y':
			print('please remove the name from the db file')
			exit()
	cons.append(create_db(name))
	

def get_entry(table, id, *args, **kwargs):
	if not cons:
		raise NoDatabasesConnected
		
	for con in reversed(cons):
		c = perform_query(table, 'ID=' + str(id), con, *args, **kwargs)
		if not c: continue
		row = c.fetchone()
		if not row: continue
		return {c.description[i][0]: row[i] for i in range(len(row)) if not row[i] == None}
		
	raise EntryNotFound(str(table) + ' ID=' + str(id))
	
def get_id_for_name(table, name):
	for con in reversed(cons):
		c = con.execute('SELECT `ID` FROM {} WHERE name=?'.format(table), [name]).fetchone()
		if not c: continue
		return c[0]
		
	raise EntryNotFound(str(table) + ' Name=' + str(id))
	
def get_children(id):
	ids = []
	for con in cons:
		ids += list(con.execute('SELECT `ability` FROM `ability_requirements` WHERE `required`=?', [id]))
	return [x[0] for x in ids]

def get_parents(id):
	ids = []
	for con in cons:
		ids += list(con.execute('SELECT `required` FROM `ability_requirements` WHERE `ability`=?', [id]))
	return [x[0] for x in ids]


@lru_cache(1)
def get_attributes():
	return json.load(open('config/attributes.json'))

@lru_cache(None)
def get_columns(table):
	return [x.split(' ')[0][1:-1] for x in open('data/templates/' + table).read().split('\n')]

def get_data(type, query, *args, **kwargs):
	all_data = {}
	
	for con in cons:
		c = perform_query(type, query, con, *args, **kwargs)
		
		if not c:
			#return {'error' :"[ERROR] {} {}".format(type, query)}, []
			continue
		
		count = 0
	
		for row in c:
			data = {c.description[i][0]: row[i] for i in range(len(row)) if not row[i] == None}
			all_data[data['ID']] = data
		
		c.close()
	
	return all_data
	

def perform_query(type, query, con, SELECT='*', include_deleted=False):
	c = con.cursor()
	WHERE = []
	
	if not SELECT == '*':
		if not 'ID' in SELECT:
			SELECT.append('ID')
		SELECT = ','.join(['`' + x + '`' for x in SELECT])
	
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
	
	if include_deleted:
		q = "SELECT " + SELECT + " FROM `{}` WHERE {} ORDER BY {}".format(type, WHERE, ORDER).format(*fields)
	else:
		q = "SELECT " + SELECT + " FROM `{}` WHERE {} AND `DELETED` IS NULL ORDER BY {}".format(type, WHERE, ORDER).format(*fields)
	#print(q)
	try:
		c.execute(q, values)
	except:
		return None
	
	return c