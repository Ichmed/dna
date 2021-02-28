from query_helper import *
from markdown2 import markdown

from builder import parse, get_widget
import query_helper

parts = {}

def attributes(data):
	for att in get_attributes()['main']:
		print(att)
		

def build(type, query, show_result_count=False):
	
	result_list = []
	
	if not (":" in query or "=" in query):
		query = 'name=' + query
	
	all_data = query_helper.get_data(type, query)
		
	result = {}
	count = 0
	for row in all_data:
		data = all_data[row]
		
		if 'parent' in data and data['parent'] in all_data: 
			#print('skipping', data['name'], 'parent', data['parent'], 'already present')
			continue
		
		editor_button = '<button class="edit" onclick="insertEditor(\'{}\', \'{}\')">Edit</button>'.format(data['ID'], type)
		#print(data)
		name = data['name']
		parent = data['parent'] if 'parent' in data else ''
		if type in ['races', 'creatures']:
			inner = build_creature(data)
		elif type in ['armor']:
			inner = build_armor(data)
		elif type in ['abilities']:
			inner = build_ability(data)
		else:
			
			#data ={'name': 'Ignite', 'other': test}
			inner = '<div style="cursor: pointer;" onclick="toggle_collapse(this.parentElement);" class="data name uncollapsable">{}</div>'.format(str(data['name']))
			
			data.pop('name')
			
			left = ""
			right = ""
			
			for key in data:
				if type == 'abilities':
					if key in ['root', 'parent', 'index', 'tags', 'skill', 'leveling', 'requires_raw']: continue
					elif key == 'cost':
						skill_cost = ''.join(['<img src="/resc/symbols/bobble_{}.png">'.format(data.get('skill')) for i in range(int(data['cost']))])
						
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
							left += '<div class="data {}">{}</div>'.format(key, res)
						else:
							right += '<div class="data {}">{}</div>'.format(key, res)

				elif type == 'rules':
					if key == 'content':
						s = parse(markdown(str(data[key]), extras=["tables"]))
						inner += '<div  class="data {}" style="clear: none;">{}</div>'.format(key, s)
				
				elif type in ['races', 'creatures']:
					
					if key == 'con':
						inner += build_creature(data)
					#	atts = [["CON", "DEX", "INT", "WIL", "INS"], ["STR", "FIN", "ING", "DEV", "CHA"], ["FRT", "AGI", "REC", "COU", "CRE"]]
					#	
					#	tbl = '<table class="wide attributes">{}</table>'
					#	tr = "<tr>{}</tr>"
					#	td = '<td><div>{}</div><div>{}</div></td>'
						
					#	inner += tbl.format("\n".join([tr.format("".join([td.format(att, data[att.lower()] if att.lower() in data else " ") for att in list])) for list in atts]))
					#elif key == 'text':
					#	s = parse(markdown(str(data[key]), extras=["tables"]))
					#	inner += '<div  class="data {}" style="clear: none;">{}</div>'.format(key, s)
				else:
					s = parse(markdown(str(data[key]), extras=["tables"]))
					inner += '<div  class="data {}" style="clear: none;">{}</div>'.format(key, s)
		
			inner += '<table style="width: 100%;"><tr style="vertical-align: top;"><td style="text-align: left; width: 80%; padding-right: 10%;">\n{}\n<td style="text-align: left; width: 20%;">\n{}\n</tr></table>'.format(left, right)
			#inner += "\n{}\n\n{}\n".format(left, right)
		
		inner += editor_button
		
		if type in ['abilities', 'rules']:
			containers, names = build(type, "parent={}".format(data['ID']))
			inner += "\n".join(list(containers.values()))
			result_list += names
		
		frame = '<div class="container_wrapper"><div collapsed=true class="collapsable container {}" id="container_{}_{}">{}</div></div>'
		#if type == "rules":
		#	result[name + "_" + parent] = frame.format(type, name, "", inner)
		#else:
		result[data['ID']] = frame.format(type, type, data['ID'], inner)
		
		count += 1
		
	#if show_result_count:
	#	result = "<p><span class=result_amount_text><span class=result_amount>{}</span> results found</span></p>".format(count) + result
	
	for key in result_list: result.pop(key, None)
	
	result_list += result.keys()
	
	return result, set(result_list)

def format_raw_data(text):
	return parse(markdown(text))

def make_def(name, data, include_name=True):
	if not name in data: return ""
	content = format_raw_data(data[name])
	return '<div class="data {}">{}{}</div>'.format(name, '<span class="label">' + name.capitalize() + ':</span>' if include_name else "", content)

def get_requirements(id):
	req = {}
	for con in cons:
		cursor = con.cursor()
		cursor.execute("SELECT `required`, `display` FROM `ability_requirements` WHERE `ability`=?", [id])
		for c in cursor:
			req[c[0]] = c[1]
			
	return req

def build_ability(data):
	
	top = '<div style="cursor: pointer;" class="container_data name uncollapsable">{}</div>'.format(str(data['name']))
	
	cost = ''.join(['<img src="/resc/symbols/bobble_{}.png">'.format(data.get('skill')) for i in range(int(data.get('cost', 0)))])
	if 'leveling' in data:
		if data['leveling'] != 'None':
			cost += '<img src="/resc/symbols/upgrade{}.png">'.format(data['leveling'])

	top += '<div class="uncollapsable skill_cost">' + cost + '</div>'
	
	
	requires = get_requirements(data['ID'])
	requires = '<div class="data requires uncollapsable">(Requires: ' + ', '.join(['<span onclick="smartlink(\'abilities\', ' + str(x) + ');event.stopPropagation();">' + requires[x] + '</span>' for x in requires]) + ')</div>' if len(requires) > 0 else ""
	
	top += requires
	
	left = []
	right = []
	
	left.append(make_def('type', data))
	left.append(make_def('ingredients', data))
	left.append(make_def('equipment', data))
	
	left.append(make_def('effect', data, False))
	left.append(make_def('result', data))
	
	
	right.append(make_def('conditions', data))
	right.append(make_def('chance', data))
	
	right.append(make_def('implement', data))
	right.append(make_def('actionpoints', data))
	right.append(make_def('manacost', data))
	right.append(make_def('staminacost', data))
	
	right.append(make_def('force', data))
	right.append(make_def('range', data))
	
	bottom =  []
	bottom.append(make_def('flavor', data))
	
	result = ""
	result += '<div class="top uncollapsable" onclick="toggle_collapse(this.parentElement);">{}</div>'.format(top)
	result += '<div class="left">{}</div>'.format(''.join(left))
	result += '<div class="right">{}</div>'.format(''.join(right))
	result += '<div class="bottom">{}</div>'.format(''.join(bottom))
	
	if not 'parent' in data and 'root' in data:
		result += get_widget('tree')(data['ID'])[0]['tree']
	
	return result

def build_armor(data):
	
	#Add name
	result = '<div style="cursor: pointer;" onclick="toggle_collapse(this.parentElement);" class="container_data name uncollapsable">{}</div>'.format(str(data['name']))
	
	result += '<div class="data text">{}</div>'.format(parse(markdown(str(data['text'] if 'text' in data else ""), extras=["tables"])))
	
	result += ''.join(['<div class="data {}">{}</div>'.format(x, data[x]) for x in ['padding', 'deflection']])
	
	return result
	
def build_creature(data):
	
	#Add name
	result = '<div style="cursor: pointer;" onclick="toggle_collapse(this.parentElement);" class="container_data name uncollapsable">{}</div>'.format(str(data['name'] if 'name' in data else ''))
	
	
	
	#Add Attributes
	result += '<div class="attributes">'
	main = get_attributes()['main']
	secondary = get_attributes()['secondary']
	
	for i in range(len(main)):
		m = list(main.keys())[i]
		mv = data[m.lower()] if m.lower() in data else ""
		
		
		a = list(secondary.keys())[i * 2]
		av = data[a.lower()] if a.lower() in data else ""
		a = "-" if not a.lower() in data else a + ':'
		try:
			if int(av) > 0: av = '+' + str(av)
		except:
			pass
		
		b = list(secondary.keys())[i * 2 + 1]
		bv = data[b.lower()] if b.lower() in data else ""
		b = "-" if not b.lower() in data else b + ':'
		try:
			if int(bv) > 0: bv = '+' + str(bv)
		except:
			pass
		
		f_string = '<div class="{} block"><div class="main {}">{} {}</div><div class="secondary {}">{} {}</div><div class="secondary {}">{} {}</div></div>'
		result += f_string.format(m, m, m, mv, a, a, av, b, b, bv)
	
	result += "</div>"
	
	
	
	result += '<div class="content">'
	#Add Text
	result += parse(markdown(str(data['text'] if 'text' in data else ""), extras=["tables"]))
	
	result += "</div>"
	result += '<div class="attributes">'
	result += '<div class="block derived health">Health: ' + (data['health'] if 'health' in data else '') + '</div>'
	result += '<div class="block derived speed">Speed: ' + (data['speed'] if 'speed' in data else '') + '</div>'
	result += "</div>"
	
	return result
	
