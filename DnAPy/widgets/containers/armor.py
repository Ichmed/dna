def build(data, cons):
	
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
	result += parse(markdown(str(data['text'] if 'text' in data else ""), extras=["tables"]), cons)
	
	result += "</div>"
	result += '<div class="attributes">'
	result += '<div class="block derived health">Health: ' + (data['health'] if 'health' in data else '') + '</div>'
	result += '<div class="block derived speed">Speed: ' + (data['speed'] if 'speed' in data else '') + '</div>'
	result += "</div>"
	
	return result