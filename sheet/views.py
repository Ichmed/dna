from django.shortcuts import render
from django.http import HttpResponse

from django.utils.safestring import mark_safe

from django.forms.models import model_to_dict

from .models import AbilityInstance, Character, InventoryItem, Resistance, SkillInstance

from rulebook.models import DamageType

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


def update_inventory(data, container=None, owner_id=None):
	content = data.pop('content', [])
	
	data['container'] = container	
	data['owner_id'] = owner_id

	# print(data)

	if 'pk' in data and data['pk'] != "":
		item = InventoryItem.objects.update_or_create(data, pk=data.get('pk'))[0]
	else:
		data.pop('pk')
		item = InventoryItem.objects.create(**data)

	for i in content:
		update_inventory(i, container=item, owner_id=None)

def store_or_update_character(request, id):
	data = json.loads(request.body)

	# for key, value in data.items():
	# 	print(key + ": " + str(value))

	u = {key: 0 if x == "" else int(x) for key, x in data['attributes'].items()}
	u.update({'name': data['name']})
	
	
	if id == 'None':
		character = Character.objects.create(**u)
		id = character.pk
	else:
		Character.objects.filter(pk=id).update(**u)
	

	for resistance, value in data.get('resistances', {}).items():
		value = 0 if value == "" else int(value)
		Resistance.objects.update_or_create({"amount": value}, owner_id=id, type_id=resistance)

	for ability in data.get('abilities', []):
		print(ability)
		if 'id' in ability and (ability['id'] == "undefined" or ability['id'] == ""):
			ability.pop('id')

		if 'id' in ability:
			AbilityInstance.objects.update_or_create(ability, owner_id=id, pk=ability['id'])
		else:
			AbilityInstance.objects.create(**ability, owner_id=id)

	for skill in data.get('skills', []):
		if not 'base_id' in skill or skill['base_id'] == "":
			skill['base_id'] = None
		# print(skill)
		SkillInstance.objects.update_or_create(skill, owner_id=id, base_id=skill['base_id'], name=skill['name'])

	for item in data.get('items', []):
		update_inventory(item, container=None, owner_id=id)


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
		if("Sense" in t):
			senses.append(a)
		elif("Movement" in t):
			moves.append(a)
		else:
			active.append(a)


	return render(request, 'sheet/character.html', 
	{
		'character': character,
		'ATT': ATT,
		'TER': TER,
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

