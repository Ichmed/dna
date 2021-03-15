from django.shortcuts import render
from django.http import HttpResponse

from django.utils.safestring import mark_safe

from django.forms.models import model_to_dict

from .models import AbilityInstance, Character, InventoryItem, Resistance, SkillInstance, InventorySlot, WeaponInstance

from rulebook.models import DamageType

from django.db.models import Q

import json

# Create your views here.


ATT = [
["CON", "STR", "FRT"],
["DEX", "AGI", "FIN"],
["INT", "ING", "REC"],
["WIL", "DEV", "COU"],
["INS", "CHA", "CRE"]
]

TER = {

'INI': "Math.floor((V('DEX') + V('INT'))/2)",
'PER': "Math.floor((V('CON') + V('INT'))/2)",
'MPA': "Math.floor((V('CON') + V('AGI'))/4)",
'MEL': "Math.floor((V('CON') + V('DEX'))/2)",
'RAN': "Math.floor((V('FIN') + V('PER'))/2)",
'PAR': "Math.floor(V('STR')/2)",
'FOR': "Math.floor((V('STR') - 10)/2)",
'CAR': "Math.floor(V('CON')/2)",
'DDG': "Math.floor((V('AGI') + V('PER'))/4)",

}

bars = {
'Health': "Math.floor(V('FRT') + 5)",
# 'Knockout Threshold' = FRT
'Stamina': "Math.floor(V('CON') + 5)",
# 'Stamina Regen' = CON / 2
'Mana': "Math.floor((V('REC') + V('DEV')) / 2)"
# 'Mana Regen' = WIL/3




}

TER = {key: mark_safe(value) for key, value in TER.items()}
bars = {key: mark_safe(value) for key, value in bars.items()}

def empty(request):

	steve = Character.objects.get(name="Steve")
	# print(model_to_dict(steve))
	# print(list(model_to_dict(x) for x in steve.abilities.all()))

	return render(request, 'sheet/character.html', 
	{
		'character': steve,
		'ATT': ATT,
		'TER': TER,
		'bars': bars,
		'skills': [model_to_dict(x) for x in steve.skills.all()],
		'abilities': [model_to_dict(x) for x in steve.abilities.all()],
	})

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def character_by_name(request, name):
	if request.method == 'POST':
		# return store_or_update_character(request)
		pass
	elif request.method == 'GET':
		character = Character.objects.get(name__iexact=name)
		return send_character(request, character)

@csrf_exempt
def character_by_id(request, id):

	if request.method == 'POST':
		return store_or_update_character(request, id)
	elif request.method == 'GET':
		if id == "new":
			character = Character()
		else:
			character = Character.objects.get(id=id)

		return send_character(request, character)


def update_inventory(data, slot_id=None, container=None, drop=False):
	content = data.pop('content', [])
	
	if drop:
		data['owner_id'] = None
		data['slot_id'] = None
	elif slot_id and data['owner_id']:
		data['slot_id'] = slot_id
	else:
		data['slot_id'] = None

	
	if data['owner_id']:
		data['container'] = container	
	else:
		data['container'] = None



	w = data['weaponinstance']
	if "id" in w:
		print(w)
		id = w.pop("id")
		if id == "":
			id = None

		data['weaponinstance'] = WeaponInstance.objects.update_or_create(w, id=id)[0]
	else: 
		data['weaponinstance'] = None

	print(data)
	if 'id' in data and data['id'] != "":
		item = InventoryItem.objects.update_or_create(data, id=data.get('id'))[0]
	else:
		data.pop('id')
		item = InventoryItem.objects.create(**data)

	for i in content:
		update_inventory(i, slot_id=None, container=item, drop=data['owner_id'] is None)

def store_or_update_character(request, id):
	data = json.loads(request.body)

	for key, value in data.items():
		print()
		print(key + ": " + str(value))

	u = {key: 0 if x == "" else int(x) for key, x in data['attributes'].items()}
	u.update({'name': data['name']})
	
	
	if id == 'None':
		character = Character.objects.create(**u)
		id = character.id
	else:
		Character.objects.filter(id=id).update(**u)
	
	InventorySlot.objects.update_or_create(owner_id=id, name="Left Hand", type="S")
	InventorySlot.objects.update_or_create(owner_id=id, name="Right Hand", type="S")
	

	for resistance, value in data.get('resistances', {}).items():
		value = 0 if value == "" else int(value)
		Resistance.objects.update_or_create({"amount": value}, owner_id=id, type_id=resistance)

	for ability in data.get('abilities', []):
		# print(ability)
		if 'id' in ability and (ability['id'] == "undefined" or ability['id'] == ""):
			ability.pop('id')
		if 'parent_id' in ability and (ability['parent_id'] == "undefined" or ability['parent_id'] == ""):
			ability.pop('parent_id')
		if 'cost' in ability and ability['base_id']:
			ability.pop('cost')
		if 'skill' in ability and ability['base_id']:
			ability.pop('skill')
		if 'leveling' in ability and ability['base_id']:
			ability.pop('leveling')

		if 'id' in ability:
			AbilityInstance.objects.update_or_create(ability, owner_id=id, id=ability['id'])
		else:
			AbilityInstance.objects.create(**ability, owner_id=id)

	for skill in data.get('skills', []):
		# print(skill)
		if not 'base_id' in skill or skill['base_id'] == "":
			skill['base_id'] = None
		print(skill)
		SkillInstance.objects.update_or_create(skill, owner_id=id, base_id=skill['base_id'], name=skill['name'])

	for slot in data['slots']:
		for item in slot['items']:
			update_inventory(item, slot_id = slot['id'])


	return HttpResponse(id)

class EMPTY:
	def __getitem__(*_):
		return ""

def send_character(request, character):
	
	senses = []
	moves = []
	active = []

	for a in character.abilities.all():
		if not a.base: continue
		t = a.base.type
		if not t is None:
			if("Sense" in t):
				senses.append(a)
			elif("Movement" in t):
				moves.append(a)
			else:
				active.append(a)
		else:
			active.append(a)

	slots = {
		"hands": character.inventory.filter(name__contains="Hand").all(),
	}

	ids = [x.id for l in slots.values() for x in l]

	slots['other'] = character.inventory.filter(~Q(id__in=ids)).all()

	# print(slots)


	# c = {
	# 	"active": active,
	# 	"moves": moves,
	# 	"senses": senses,
	# 	"skills": character.skills.filter(DELETED=None).all()
	# 	"abilities": 
	# }


	return render(request, 'sheet/character.html', 
	{
		'character': character,
		'ATT': ATT,
		'TER': TER,
		'slots': slots,
		'bars': bars,
		'senses': senses,
		'moves': moves,
		'active': active,
		'damage_types': DamageType.objects.all(),
		'empty': EMPTY(),
		# 'skills': [model_to_dict(x) for x in character.skills.all()],
		# 'abilities': [model_to_dict(x) for x in character.abilities.all()],
		# 'wounds': [model_to_dict(x) for x in character.wounds.all()],
		# 'inventory': [model_to_dict(x) for x in character.inventory.all()],
		# 'notes': [model_to_dict(x) for x in character.notes.all()],
	})

def list_characters(request):
	return render(request, 'sheet/welcome.html', {
		"characters": Character.objects.all()
	})

