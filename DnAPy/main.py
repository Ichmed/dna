import sqlite3
import handlers as h
import os
import server
import sys
from sheet import SheetHandler
import json5
import images
import re
import query_helper

def build_resources():
	skills = json5.load(open('config/skills.json'))
	
	skills_css = open('resc/generated/skills.css', mode='w')
	root = ""
	for skill in skills:
		print('Building resources for skill', skill)
		data = ".skill_" + skill + " .skill_color {\n backgroundcolor: " + skills[skill]['color'] + ";\n}\n"
		root += "--" + skill + "-color: " + skills[skill]['color'] + ";\n"
		skills_css.write(data)
		images.build_bobble(skill, skills[skill]['color'], no_icon=skills[skill].get('type') == 'pseudo')
	skills_css.write(':root {\n' + root + "}")
	
	skills_css.close()


if __name__ == "__main__":
	
	if '--rebuild' in sys.argv: 
		print('Rebuilding Resources...')
		build_resources()
		print('Done')
		
	import widgets.tree_2 as tree_2
	
	print([str(x) for x in tree_2.Tree(306).node_layers.values()])
	
	if '--only-init' in sys.argv: exit()
	
	print('Registering hanlders...')
	
	server.register_handler('/api', h.API())
	server.register_handler('/resc', h.Resource())
	server.register_handler('/', h.Resource())
	server.register_handler('/search/', h.Search())
	server.register_handler('/sheet', SheetHandler())
	
	re.compile(r'/$(.*)')
	
	server.register_handler(r'/$', server.Redirect('/search/rules?name:'))
	
	print('Done')
	
	server.run(8000)