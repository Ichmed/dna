import sqlite3, os

def create_db(name, overwrite=False):
	name = 'data/' + name + '.db'
	if os.path.isfile(name):
		if not overwrite:
			raise Exception('"' + name + '" already exists')
		else:
			os.remove(name)
			
	connection = sqlite3.connect(name)
	cursor = connection.cursor()
	
	for template in os.listdir('data/templates'):
		cursor.execute('CREATE TABLE IF NOT EXISTS ' + open('data/templates/' + template).read())
		print(cursor.fetchone())
		
	cursor.close()
	return connection

def get_tables():
	open('data/db').read().split('\n')
	
def set_tables(list):
	open('data/db').write("\n".join(list))
	
def get_names():
	return open('config/tables').read().split('\n')
	
if __name__ == '__main__':
	create_db('test')