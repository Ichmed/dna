from django.db.models import *
from colorfield.fields import ColorField

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .bobbles import build_bobble

class Expansion(Model):
	name = CharField(max_length=100)
	
class RulebookEntry(Model):
	name = CharField(max_length=100)
	tags = CharField(max_length=2000, blank=True, null=True)
	flavor = CharField(max_length=2000, blank=True, null=True)
	expansion = ForeignKey(Expansion, default=0, on_delete=CASCADE)
	#Used for soft-delete
	DELETED = DateTimeField(default=None, null=True, blank=True)
	
	class Meta:
		abstract = True
	
	def __str__(self):
		return self.name
		
# Create your models here.

class Skill(RulebookEntry):
	isPseudo = BooleanField(default=False)
	color = ColorField(default="#FF0000")

@receiver(post_save, sender=Skill)
def update_bobbles(sender, instance, created, **kwargs):
	build_bobble(instance)


class Ability(RulebookEntry):
	effect = CharField(max_length=2000)
	parent = ForeignKey('self', on_delete=CASCADE, blank=True, null=True, related_name='children')
	
	#Requirements
	requires = ManyToManyField('self', blank=True, symmetrical=False, through="AbilityRequirement", through_fields=('ability', 'requires'), related_name='required')
	requires_raw = CharField(max_length=1000, blank=True, null=True)
	
	root = ForeignKey('self', on_delete=CASCADE, blank=True, null=True, related_name='+')
	index = IntegerField(blank=True, null=True)
	
	cost = IntegerField(default=0, null=True)
	skill = ForeignKey(Skill, on_delete=CASCADE, blank=True, null=True)
	leveling = CharField(max_length=45, blank=True, null=True)
	
	type = CharField(max_length=100, blank=True, null=True)
	
	actionpoints = CharField(max_length=100, blank=True, null=True)
	manacost = CharField(max_length=100, blank=True, null=True)
	staminacost = CharField(max_length=100, blank=True, null=True)
	
	equipment = CharField(max_length=100, blank=True, null=True)
	implement = CharField(max_length=100, blank=True, null=True)
	ingredients = CharField(max_length=2000, blank=True, null=True)
	conditions = CharField(max_length=2000, blank=True, null=True)	
	
	chance = CharField(max_length=100, blank=True, null=True)
	quality = CharField(max_length=100, blank=True, null=True)
	
	duration = CharField(max_length=100, blank=True, null=True)
	range = CharField(max_length=100, blank=True, null=True)
	force = CharField(max_length=100, blank=True, null=True)

	effect = CharField(max_length=2000, blank=True, null=True)
	result = CharField(max_length=2000, blank=True, null=True)
	
	
	def __str__(self):
		return self.name + (" [" + str(self.parent) + "]" if self.parent else "")
		
	
	class Meta:
		ordering = ("root_id", "index")
		
@receiver(post_save, sender=Ability)
def update_requirements(sender, instance, **kwargs):
	if instance.requires_raw == None or instance.requires_raw == "": return
	reqs = instance.requires_raw.split(';')
	raw_result = []
	changed = {}
	instance.requires.clear()
	for r in reqs:
		if r == "": continue
		r = r.split('|')
		if len(r) == 2:
			name, display = r
		else:
			name = display = r[0]
		try:
			instance.requires.add(Ability.objects.get(name=name, DELETED=None), through_defaults={'display': display})
		except Ability.MultipleObjectsReturned:
			instance.requires.add(Ability.objects.filter(name=name, DELETED=None)[0], through_defaults={'display': display})
		except Ability.DoesNotExist:
			raw_result.append(name)
	
	
	changed['requires_raw'] = "\n".join(raw_result)

	if instance.parent:
		changed['root'] = instance.parent.root_id
	else:	
		cursor = instance
		print(cursor.requires)
		while cursor.requires.all():
			cursor = list(cursor.requires.all())[0]
		changed['root'] = cursor.id
	
	Ability.objects.filter(id=instance.id).update(**changed)


class AbilityRequirement(Model):
	ability = ForeignKey(Ability, on_delete=CASCADE, related_name="requirement")
	requires = ForeignKey(Ability, on_delete=CASCADE, related_name="+")
	display = CharField(max_length=200)
	
class Rule(RulebookEntry):
	parent = ForeignKey('self', on_delete=CASCADE, blank=True, null=True, related_name="children")
	content = CharField(max_length=10000, blank=True, null=True)
	content_short = CharField(max_length=250, blank=True, null=True)
	priority = IntegerField(default=0)
	
class Item(RulebookEntry):
	text = CharField(max_length=2000)
	weight = CharField(max_length=200, blank=True, null=True)
	cost = CharField(max_length=200, blank=True, null=True)

class Enchantment(RulebookEntry):
	text = CharField(max_length=2000)
	strength = CharField(max_length=200)
	
class Feature(RulebookEntry):
	text = CharField(max_length=2000)

class Substance(RulebookEntry):
	text = CharField(max_length=2000)
	density = FloatField(default=1.0)

class Material(Substance):
	category = CharField(max_length=200)
	deflection = FloatField(default=0)
	padding = FloatField(default=0)

class DamageType(RulebookEntry):
	name = CharField(max_length=200)

class Weapon(RulebookEntry):
	skill = ForeignKey(Skill, on_delete=CASCADE, blank=True, null=True)
	
	damage_base = IntegerField(default=0)
	damage_dice = IntegerField(default=0)
	dice_type = CharField(max_length=3, default="d6")
	damage_type = CharField(max_length=3, default="P", choices=[("P", "Piercing"), ("B", "Blunt")])
	
	force = IntegerField(default=0)
	force_modifier = IntegerField(default=1)
	
	parry = IntegerField(default=0)
	
	cost = IntegerField(default=6)
	cost_reload = IntegerField(default=3, blank=True, null=True)
	
	weight = IntegerField(default=500)
	min_str = IntegerField(default=None, null=True, blank=True)
	
	min_range = IntegerField(default=None, null=True, blank=True)
	max_range = IntegerField(default=None, null=True, blank=True)

class Armor(RulebookEntry):
	deflection = FloatField(default=0)
	padding = FloatField(default=0)
	
	text = CharField(max_length=2000, default=None, null=True, blank=True)

	
class RulebookEntryWithStats(RulebookEntry):
	class Meta:
		abstract = True
	
	CON = CharField(max_length=200)
	STR = CharField(max_length=200)
	FRT = CharField(max_length=200)
	
	DEX = CharField(max_length=200)
	AGI = CharField(max_length=200)
	FIN = CharField(max_length=200)
	
	INT = CharField(max_length=200)
	ING = CharField(max_length=200)
	REC = CharField(max_length=200)
	
	WIL = CharField(max_length=200)
	DEV = CharField(max_length=200)
	COU = CharField(max_length=200)
	
	INS = CharField(max_length=200)
	CHA = CharField(max_length=200)
	CRE = CharField(max_length=200)
	
	
class Race(RulebookEntryWithStats):
	text = CharField(max_length=2000)


class Creature(RulebookEntryWithStats):
	text = CharField(max_length=2000)
	
