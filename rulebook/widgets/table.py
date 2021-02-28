import builder, query_helper

def build(type, query, title=None, limit=None, wide="True"):
	
	if limit: limit = [s.strip() for s in limit.split(",")]
	
	
	td = '<td class="table_data_{}">{}</td>'
	tr = []
	
	header = ""
	
	data = query_helper.get_data(type, query)
	columns = limit if limit else query_helper.get_columns(type)
	
	header = '<tr>{}</tr>'.format("".join(['<th>{}</th>'.format(key.capitalize()) for key in columns if not limit or key in limit]))
	
	for r in data.values():
		row = []
		for desc in columns:
			if limit and not desc in limit: continue
			if not desc in r: continue
			elif desc == "name":
				d = builder.get_widget('link')(type, r[desc])[0]['link']
			elif desc == "skill":
				d = '<img src="/resc/symbols/bobble_' + r[desc] + '.png">'
			else:
				d = r[desc]
			row.append(td.format(desc, d))
		tr.append('<tr>{}</tr>'.format("".join(row)))
		
	
	tr = "\n".join(tr)
	return {"table": '<div class="widget_table {}">{}<table>{}\n{}</table></div>'.format( "wide" if wide == "True" else "", '<h2>' + title + '</h2>' if title else "", header, tr)}, []
