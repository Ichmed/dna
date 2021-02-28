import query_helper, json

class SheetHandler:
	def handle(self, url):
		
		attributes = query_helper.get_attributes()
		#data = json.load('characters/' + url + '.json')
		
		html = """<html>
	<head>	
		<link rel="stylesheet" type="text/css" href="/resc/sheet.css">
	</head>
	<body>{}</body>
</html>"""


		box = '<div class="{name} block {type}" title={full_name}><span class="{name} label">{name}</span><input class="{name} input"></div>'
		
		
		#Add Attributes
		result = '<div class="attributes">'
		main = attributes['main']
		secondary = attributes['secondary']
		input = '<input>'
		
		for i in range(len(main)):
			m = list(main.keys())[i]
			a = list(secondary.keys())[i * 2]			
			b = list(secondary.keys())[i * 2 + 1]
			
			f_string = '<div class="{m} block"><div class="main {m}"><span class="label">{m}</span> {i}</div><div class="secondary {a}"><span class="label">{a}</span> {i}</div><div class="secondary {b}"><span class="label">{b}</span> {i}</div></div>'
			result += f_string.format(m=m, a=a, b=b, i=input)
		
		result += "</div>"
		
		frame = '<div id="frame">{ATT}</div>'
		
		boxes = {}
		boxes['ATT'] = result#'<div class="attributes">{}</dvi>'.format("\n".join([box.format(name=x, **attributes['main'][x], type='main') for x in attributes['main']]))
		
		html = html.format(frame.format(**boxes))
		
		return 200, html.encode()