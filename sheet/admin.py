from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(Character)
admin.site.register(AbilityInstance)
admin.site.register(SkillInstance)
admin.site.register(Note)
admin.site.register(InventoryItem)
admin.site.register(Wound)
admin.site.register(Resistance)
