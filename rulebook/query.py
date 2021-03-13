from rulebook.models import *

from django.db.models import Q
from django.http import Http404

import re

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
	try:
		return models[name]
	except KeyError:
		raise Http404("This Category does not exist")


def perform_query(table, query, page=-1):
	
	model = get_model_for_name(table.lower())
	manager = model.objects

	print(query)

	Qs = []
	excludes=[]
	filters = {}
	objs = None
	filters['DELETED'] = None
	if query:
		for sub in query.split(";"):
			if sub == "": continue
			

			for q in sub.split("+"):
				key, mode, value = re.match(r"\s*(\w*?)\s*([:=!])\s*([\w, ]*)", q).groups()


				if value == "0": value = None

				# print(key, mode, value)

				if key.lower() == "requires":
					reqs = value.split(',')
					if mode == ":":
						Qs.append(Q(requires__in=reqs) | Q(requires=None))
						Qs.append(Q(parent=None))
					if mode == "=":
						# Qs.append(Q(num_reqs__lte=len(reqs)))
						# Qs.append(Q(requires__in=reqs))
						Qs += [Q(requires=r) for r in reqs]
						manager = manager.annotate(num_reqs=Count('requires'))
						# excludes.append(~Q(requires__in=reqs))
						Qs.append(Q(parent=None))
					if mode == "!":
						# Qs.append(Q(num_reqs__lte=len(reqs)))
						# Qs.append(Q(requires__in=reqs))
						Qs += [Q(requires=r) | Q(requires=None) for r in reqs]
						manager = manager.annotate(num_reqs=Count('requires'))
						# excludes.append(~Q(requires__in=reqs))
				else:
					if mode == "=":
						filters[key] = value
					elif mode == ":":
						filters[key + "__contains"] = value

			if objs: objs |= manager.filter(*Qs, **filters).exclude(*excludes).all()
			else: objs = manager.filter(*Qs, **filters).exclude(*excludes).all()
	elif get_model_for_name(table) in [Ability, Rule]:
		#Query is None, all entries will be returned.
		#Exclude all objects with parents (Upgrades etc), they will be removed anyway
		Qs = [Q(parent=None)]
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
