from django.template import loader

def build(*data):
	context = {"rows": [{"cost": x, "text": y} for x, y in chunks(data, 2)]}
	return loader.get_template("rulebook/widgets/crafting.html").render(context)

def chunks(lst, n):
	"""Yield successive n-sized chunks from lst."""
	for i in range(0, len(lst), n):
		yield lst[i:i + n]