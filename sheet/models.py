from django.db.models import *

# Create your models here.

class Character(Model):
	name = CharField(max_length=255)
	race = ForeignKey('rulebook.Race', on_delete=CASCADE)
	
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

	INI_mod = IntegerField(default=10)
	PER_mod = IntegerField(default=10)
	MPA_mod = IntegerField(default=10)

	MEL_mod = IntegerField(default=10)
	RAN_mod = IntegerField(default=10)
	PAR_mod = IntegerField(default=10)
	FOR_mod = IntegerField(default=10)

	CAR_mod = IntegerField(default=10)
	DDG_mod = IntegerField(default=10)

	Health_mod = IntegerField(default=10)
	Health = IntegerField(default=10)
	Stamina_mod = IntegerField(default=10)
	Stamina = IntegerField(default=10)
	Mana_mod = IntegerField(default=10)
	Mana = IntegerField(default=10)
	
	def __str__(self):
		return self.name


class AbilityInstance(Model):
	base = ForeignKey('rulebook.Ability', blank=True, null=True, on_delete=CASCADE)
	name = CharField(max_length=255)
	level = IntegerField()
	owner = ForeignKey(Character, related_name='abilities', on_delete=CASCADE)
	

	def __str__(self):
		return self.name + " " + str(self.pk)

class SkillInstance(Model):
	base = ForeignKey('rulebook.Skill', blank=True, null=True, on_delete=CASCADE)
	name = CharField(max_length=255)
	level = IntegerField(default=1)
	granted = IntegerField(default=0)
	owner = ForeignKey(Character, related_name='skills', on_delete=CASCADE)
	
	def __str__(self):
		return self.name + " " + str(self.pk)

class InventoryItem(Model):
	base = ForeignKey('rulebook.Item', blank=True, null=True, on_delete=CASCADE)
	name = CharField(max_length=255)
	text = CharField(max_length=2000, blank=True)
	owner = ForeignKey(Character, blank=True, null=True, on_delete=CASCADE, related_name='inventory')
	container = ForeignKey('self', blank=True, null=True, on_delete=CASCADE, related_name='content')
	weight = IntegerField(default=0)
	amount = IntegerField(default=1)
	
	def __str__(self):
		return self.name + " " + str(self.pk)

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
