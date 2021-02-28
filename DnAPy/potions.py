def count_list(list):
	r = {}
	for e in list:
		r[e] = r[e] + 1 if e in r else 1
	return r

	
elements = ['mortis', 'phlogiston', 'sangus', 'armriel']

def get_number_word(i):
	d = {1: "mono", 2: "di", 3: "tri", 4: "quad", 5: "penta", 6: "hexa", 7: "septo", 8: "octa", 9: "nona", 10: "deca"}
	
	if i in d: return d[i]
	return str(i)

def build_name(dict):
	return "-".join([get_number_word(dict[e]) + '-' + str(e).capitalize() for e in elements if e in dict])
	

d = count_list(['phlogiston', 'phlogiston', 'armriel'])

print(build_name(d))