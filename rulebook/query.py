from rulebook.models import *
from django.db.models import Q

from .templatetags.cache import push, put, pop

class UnableToQuery(Exception):
	pass

def get_model_for_name(name):
	models = {
		"ability": Ability, "abilities": Ability,
		"rule": Rule, "rules": Rule,
		"armor": Armor,
		"substance": Substance,
		"material": Material,
		"race": Race, "races": Race,
		"weapons": Weapon, "weapon": Weapon,
		"enchantment": Enchantment,
		"items": Item, "item": Item,
		"feature": Feature,
		"skill": Skill,
		"expansion": Expansion,
		"creature": Creature, "creatures": Creature,
	}
	
	return models[name]


def perform_query(table, query):
	
	manager = get_model_for_name(table.lower()).objects
		
	Qs = []
	filters = {}
	objs = None
	filters['DELETED'] = None
	if query:
		for sub in query.split(";"):
			if sub == "": continue
			for q in sub.split("+"):
				if "=" in q:
					filters[q.split("=")[0] + "__iexact"] =  q.split("=")[1]
				elif ":" in q:
					filters[q.split(":")[0] + "__contains"] =  q.split(":")[1]
			if objs: objs |= manager.filter(*Qs, **filters).all()
			else: objs = manager.filter(*Qs, **filters).all()
	elif get_model_for_name(table) in [Ability, Rule]:
		#Query is None, all entries will be returned.
		#Exclude all objects with parents (Upgrades etc), they will be removed anyway
		Qs = [~Q(type=None)]
		objs = manager.filter(*Qs, **filters).all()
	else: 
		objs = manager.all()

		
	try:
		if len(objs) > 1 and hasattr(objs[0], 'parent'):
			counter = 0
			b = True
			while b:
				b = False
				for o in objs:
					p = o.parent
					for _ in range(counter):
						if p == None:
							continue
						p = p.parent
					if p and p in objs:
						objs = objs.exclude(id=o.id)
						b = True
				counter += 1
		for o in objs:
			push("data:" + table + ":" + str(o.id))
			put("")
			pop()

		return objs
	except Exception as e:
		print("Could not perform query " + table + " " + query)
		raise e
