import query_helper
import markdown2 as mk

def build(*data):
	result = "<table class='crafting'>" + "\n".join("<tr><td class='cost'>{}</td><td class='inner'>{}</td>".format(x, mk.markdown(y) if y else "") for x, y in chunks(data, 2)) + "</table>"
	return {"crafting": result}, []

def chunks(lst, n):
	"""Yield successive n-sized chunks from lst."""
	for i in range(0, len(lst), n):
		yield lst[i:i + n]