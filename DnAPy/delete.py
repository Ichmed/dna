import sqlite3

con = sqlite3.connect('dna.db')
c = con.cursor()

c.execute('DELETE FROM `ability_requirements` WHERE `ability`=?', ["Test"])
con.commit()