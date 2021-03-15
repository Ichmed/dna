from django.db.models import *

# Create your models here.

class Character(Model):
	name = CharField(max_length=255)
	race = ForeignKey('rulebook.Race', on_delete=CASCADE, blank=True, null=True)
	
	CON = IntegerField(default=10)
	STR_mod = IntegerField(default=0)
	FRT_mod = IntegerField(default=0)
	
	DEX = IntegerField(default=10)
	AGI_mod = IntegerField(default=0)
	FIN_mod = IntegerField(default=0)
	
	INT = IntegerField(default=10)
	ING_mod = IntegerField(default=0)
	REC_mod = IntegerField(default=0)
	
	WIL = IntegerField(default=10)
	DEV_mod = IntegerField(default=0)
	COU_mod = IntegerField(default=0)
	
	INS = IntegerField(default=10)
	CHA_mod = IntegerField(default=0)
	CRE_mod = IntegerField(default=0)

	INI_mod = IntegerField(default=0)
	PER_mod = IntegerField(default=0)
	MPA_mod = IntegerField(default=0)

	MEL_mod = IntegerField(default=0)
	RAN_mod = IntegerField(default=0)
	PAR_mod = IntegerField(default=0)
	FOR_mod = IntegerField(default=0)

	CAR_mod = IntegerField(default=0)
	DDG_mod = IntegerField(default=0)

	Health_mod = IntegerField(default=0)
	Health = IntegerField(default=10)
	Stamina_mod = IntegerField(default=0)
	Stamina = IntegerField(default=10)
	Mana_mod = IntegerField(default=0)
	Mana = IntegerField(default=10)
	
	def __str__(self):
		return self.name


class AbilityInstance(Model):
	base = ForeignKey('rulebook.Ability', blank=True, null=True, on_delete=CASCADE)
	parent = ForeignKey('self', on_delete=CASCADE, blank=True, null=True, related_name="children")
	name = CharField(max_length=255)
	level = IntegerField()
	owner = ForeignKey(Character, blank=True, null=True, related_name='abilities', on_delete=CASCADE)
	

	def __str__(self):
		return self.name + " " + str(self.pk)

class SkillInstance(Model):
	base = ForeignKey('rulebook.Skill', blank=True, null=True, on_delete=CASCADE)
	name = CharField(max_length=255)
	level = IntegerField(default=1)
	granted = IntegerField(default=0)
	owner = ForeignKey(Character, null=True, related_name='skills', on_delete=CASCADE)
	
	def __str__(self):
		return self.name + " " + str(self.pk)

class InventorySlot(Model):
	owner = ForeignKey(Character, blank=True, null=True, on_delete=SET_NULL, related_name='inventory')
	name = CharField(max_length=255)
	type = CharField(max_length=1, choices=[("S", "Single"), ("M", "Multi")])

	def __str__(self):
		return f"{self.owner} - {self.name} ({self.type})"


class InventoryItem(Model):
	name = CharField(max_length=255)
	slot = ForeignKey(InventorySlot, related_name='items', blank=True, null=True, on_delete=SET_NULL)
	owner = ForeignKey(Character, blank=True, null=True, on_delete=SET_NULL, related_name='items')

	base = ForeignKey('rulebook.Item', blank=True, null=True, on_delete=CASCADE)
	text = CharField(max_length=2000, blank=True)
	container = ForeignKey('self', blank=True, null=True, on_delete=CASCADE, related_name='content')
	weight = IntegerField(default=0)
	amount = IntegerField(default=1)
	
	def __str__(self):
		return self.name + " " + str(self.pk)

class WeaponInstance(InventoryItem):

	base_weapon = ForeignKey('rulebook.Weapon', blank=True, null=True, on_delete=CASCADE)
	skill = ForeignKey('rulebook.Skill', blank=True, null=True, on_delete=CASCADE)

	hit = CharField(default="", blank=True, max_length=2)
	force = CharField(default="", blank=True, max_length=2)
	parry = CharField(default="", blank=True, max_length=2)
	cost = CharField(default="", blank=True, max_length=2)

	flat_damage = CharField(default="", blank=True, max_length=2)
	dice_damage = CharField(default="", blank=True, max_length=2)
	damage_type = CharField(default="", blank=True, max_length=1)


	isRanged = BooleanField(default=False)
	range = CharField(default="", blank=True, max_length=2)


class Resistance(Model):
	owner = ForeignKey(Character, related_name='resistances', on_delete=CASCADE)
	type = ForeignKey('rulebook.DamageType', on_delete=CASCADE)
	amount = IntegerField(default=0)

	def __str__(self):
		return f"{self.owner} {self.type} {self.amount}"

class Wound(Model):
	type = ForeignKey('rulebook.DamageType', on_delete=CASCADE)
	size = IntegerField()
	healed = IntegerField()
	state = CharField(default="F", max_length=1, choices=[('F', 'Fresh'), ('T', 'Treated'), ('O', 'Old')])
	owner = ForeignKey(Character, related_name='wounds', on_delete=CASCADE)
	
	def __str__(self):
		return f"{self.owner} {self.healed}/{self.size}({self.type})"

class Note(Model):
	owner = ForeignKey(Character, related_name='notes', on_delete=CASCADE)
	text = CharField(max_length=2000)
	expiration = IntegerField()
	
	def __str__(self):
		return str(self.pk) + " " + self.text 
