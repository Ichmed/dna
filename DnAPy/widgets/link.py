import query_helper

def build(type, target, text=None):
	if not text: 
		text = target
	
	exists = False
	if not (":" in target or "=" in target):
		query = 'name=' + target
	else:
		query = target
	
	data = list(query_helper.get_data(type, query).values())
	if not data:
		return {"link": '<span class="brokenLink">{}</span>'.format(text)}, []
	else:
		data = data[0]
		popup_text = ""
		if 'content_short' in data:
			popup_text = data['content_short']
		else:
			if 'content' in data: 
				popup_text = data['content']
			elif 'text' in data: 
				popup_text = data['text']
			elif 'effect' in data: 
				popup_text = data['effect']
			elif 'result' in data: 
				popup_text = data['result']
			
			if len(popup_text) > 200 or popup_text == "":
				popup_text = popup_text[:200] + '...'

		return {"link": '<span class="smartlink tooltip" onClick="smartlink(\'{}\', \'{}\');">{}<span class="tooltiptext">{}</span></span>'.format(type, data['ID'], text, popup_text)}, []
