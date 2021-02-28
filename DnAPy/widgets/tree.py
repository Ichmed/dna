from functools import lru_cache

def calc_width(root, children, width={}):
	width = {}
	w = 0
	for c in children[root]:
		if c in width: continue
		width = {**width, **calc_width(c, children, width)}
		w += width[c]
	if w == 0: w = 1
	width[root] = w
	
	return width

	
cache = {}
#@lru_cache(maxsize=None)
def build(cons, root, distance = 30, size = 20):
	
	root_name = root
	
	for con in cons:
		for c in con.execute('SELECT ID FROM abilities WHERE name=?', [root]):
			root = c[0]
	
	if root in cache:
		return cache[root]
	
	# A list containing the parents for each node
	parents = {}
	done = []
	todo = [root]
	
	# A list containing the children for each node
	children = {}
	
	names={root: root_name}
	
	while len(todo) > 0:
		for con in cons:
			cursor = con.cursor()
			name = todo.pop()
			done += [name]
			cursor.execute("SELECT * FROM `ability_requirements` WHERE ability=?", [name])
			p = [x[1] for x in cursor]
			parents[name] = p
			
			cursor.execute("SELECT * FROM `ability_requirements` WHERE required=?", [name])
			c = [x[0] for x in cursor]
			children[name] = c
						
			todo = [x for x in set(list(todo) + p + c) if x not in done]
			
			cursor.close()
	
	width = calc_width(root, children)
	coords = {}
	
	for node in done:
		c_width = min(1, sum([width[x] if x in width else 1 for x in children[node]]))
		
		if not node in coords:
			coords[node] = [0, 0]
		pos = coords[node]
		x = pos[0] - (c_width - 1) / 2.0
		
		for parent in parents[node]:
			if not parent in coords:
				coords[parent] = [x, pos[1] + 1]
				x += width[parent] if parent in width else 1
			else:
				if coords[parent][1] < pos[1]:
					coords[parent][1] += 1
					#coords[parent][0] = x
					
		x = pos[0] - (c_width - 1) / 2.0
		
		for child in children[node]:
			if not child in coords:
				coords[child] = [x, pos[1] - 1]
				x += width[child] if child in width else 1
			else:
				if coords[child][1] > pos[1]:
					coords[child][1] -= 1
					#coords[child][0] = x
	
	min_y = 0
	max_y = 1
	min_x = 0
	max_x = 1
	for c in coords:
		c = coords[c]
		if c[0] < min_x: min_x = c[0]
		if c[0] > max_x: max_x = c[0]
		
		if c[1] < min_y: min_y = c[1]
		if c[1] > max_y: max_y = c[1]
	
	
	width = (max_x - min_x + 1) * distance
	height = (max_y - min_y) * distance
	
	lines = []
	
	for x in done:
		for p in parents[x]:
			pos = [(coords[x][0] - min_x) * distance + size/2, height - (coords[x][1] - min_y + 1) * distance, (coords[p][0] - min_x) * distance + size/2, height - (coords[p][1] - min_y + 1) * distance + size]
			lines.append("\n".join(['<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="black" />'.format(*pos) for p in parents[x]]))
	
	bobbles = []
	
	for x in coords:
		for con in cons:
			cursor = con.cursor()
			ID, name, skill = cursor.execute("SELECT `ID`, `name`, `skill` FROM `abilities` WHERE ID=?", [x]).fetchone()
			pos = [ID, name, skill, (coords[x][0] - min_x) * distance, height - (coords[x][1] - min_y + 1) * distance]
		
			bobbles.append('<img onclick="smartlink(\'abilities\', \'{}\')" class="skilltree_bobble" title="{}" src="/resc/symbols/bobble_{}.png" style="position: absolute; left:{}; top:{}">'.format(*pos))
			cursor.close()
	bobbles = "\n".join(bobbles)
	
	lines = "\n".join(lines)
	
	
	result = {'tree': '<div class="skilltree"><div><svg style="position: relative; height:{}; width:{};">{}</svg>\n{}</div></div>'.format(height, width, lines, bobbles)}, []
	
	cache[root] = result
	return result
