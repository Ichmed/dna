import pandas, sqlite3

#name = 'ability_requirements'

#df = pandas.read_csv('{}.csv'.format(name), sep=";")

con = sqlite3.connect('dna.db')
c = con.cursor()

table = """
`potions` (
  `composition` tinytext NOT NULL,
  `parent` tinytext,
  `priority` tinytext,
  `name` tinytext NOT NULL,
  `effect` mediumtext,
  `delay` mediumtext,
  `duration` mediumtext,
  `application` mediumtext,
  `color` tinytext,
  `aroma` mediumtext,
  `appearance` mediumtext,
  PRIMARY KEY (`composition`)
)"""

#c.execute("CREATE TABLE {}".format(table))

c.execute("INSERT INTO potions (composition, name) VALUES ('Test', 'Test')".format(table))

#for row in df.where(df.notnull(), 'NULL').values.tolist():
#	
#	#if row[13] == 'NULL':
#	#	row[13] = ''
#		
#		
#	cols = ', '.join(["`{}`".format(str(x)) for x in df.columns.tolist()])
#	values = ', '.join(["'{}'".format(str(x)) if not x == 'NULL' else 'NULL' for x in row])
#	
#	insert = "REPLACE INTO {} ({}) VALUES ({})".format(name, cols, values)
#	
#	print(insert)
#	
#	c.execute(insert)

con.commit()