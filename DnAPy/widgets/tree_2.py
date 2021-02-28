import query_helper

class Node:
	def __init__(self, id, **kwargs):
		self.id = id
		self.fields = kwargs
		self.parents = {}
		self.children = {}
		self.layer = None
		self.pos_x = 0
		self.width = None
		
	def add_child(self, child):
		self.children[child.id] = child
		child.parents[self.id] = self
	
	def add_parent(self, parent):
		self.parents[parent.id] = parent
		parent.children[self.id] = self
	
	def calc_position(self, direction='DOWN'):
		i = 0
		if direction == 'UP':
			for n in self.parents.values():
				if n.layer == None: n.layer = self.layer - 1
				else: n.layer = min(self.layer - 1, n.layer)
				n.pos_x = self.pos_x + i
				i += n.calc_width()
				n.calc_position(direction)
		else:
			for n in self.children.values():
				if n.layer == None: n.layer = self.layer + 1
				else: n.layer = max(self.layer + 1, n.layer)
				n.pos_x = self.pos_x + i
				i += n.calc_width()
				n.calc_position(direction)
				
				
	def calc_width(self):
		if not self.width: self.width = max(sum([c.calc_width() for c in self.children.values()]), 1)
		return self.width
		
class Tree:
	
	def __init__(self, id):
		self.nodes = {}
		self.node_layers = {}
		self.head = self.tree_from_root_down(id)
		self.tree_from_root_up(id)
		
		self.head.layer = 0
		
		self.head.calc_position('UP')
		self.head.calc_position('DOWN')
		
		for node in self.nodes.values():
			self.node_layers.setdefault(node.layer, []).append(node)
	
	def add_node(id, **kwargs):
		n = Node(id, **kwargs)
		self.nodes[id] = n
		return n
		
	def node_from_id(self, id):
		data = query_helper.get_entry('abilities', id)
		return Node(data['ID'], **data)

	def tree_from_root_down(self, id):
		node = self.nodes.setdefault(id, self.node_from_id(id))
		
		for child in query_helper.get_children(id):
			c_node = self.tree_from_root_down(child)
			self.nodes[id].add_child(c_node)
			
		return node
		
	def tree_from_root_up(self, id):
		node = self.nodes.setdefault(id, self.node_from_id(id))
		
		for child in query_helper.get_parents(id):
			c_node = self.tree_from_root_up(child)
			self.nodes[id].add_parent(c_node)
			
		return node

def build(root):
	try:
		id = int(root)
	except:
		id = query_helper.get_id_for_name('abilities', root)
	
	t = Tree(id)
	
	result = '<div class="skilltree" style="width: {};"><div><svg style="position: relative;">{}</svg>\n{}</div></div>'
	
	bobbles = []
	lines = []
	
	min_layer = min(t.node_layers.keys())
	
	for layer in t.node_layers:
		for node in t.node_layers[layer]:
			x = (node.pos_x + node.calc_width() / 2) * 30
			bobbles.append('<img onclick="smartlink(\'abilities\', \'{}\')" class="skilltree_bobble" title="{}" style="position: absolute; left:{}; top:{};" src="/resc/symbols/bobble_{}.png">'.format(node.fields['ID'], node.fields['name'], x, (layer - min_layer) * 30, node.fields.get('skill', 'None')))
			
			lines.append("\n".join(['<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="black" />'.format((p.pos_x + p.calc_width() / 2) * 30 - 10, (p.layer - min_layer) * 30, x - 10, (node.layer - min_layer) * 30 - 20) for p in node.parents.values()]))
			
	return {'tree': result.format(t.head.calc_width() * 30 + 40, ''.join(lines), ''.join(bobbles))}, []
	
	
	
	
if __name__ == '__main__':
	A = add_node('A')
	B = add_node('B')
	C = add_node('C')
	D = add_node('D')
	
	node_from_id(1)
	
	A.add_child(B)
	B.add_child(C)
	A.add_child(D)
	
	print(nodes)
	print([nodes[n].id + ':' + str(nodes[n].calc_layer()) for n in nodes])