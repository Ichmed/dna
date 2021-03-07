from django.urls import path

from . import views

urlpatterns = [
	path('', views.list_characters, name='list'),
	path('character/<name>', views.character_by_name, name='character'),
	path('character/id/<id>', views.character_by_id, name='character'),
]