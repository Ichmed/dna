from django.urls import path

from . import views

urlpatterns = [
	path('', views.empty, name='empty'),
	path('character/<name>', views.character_by_name, name='character'),
	path('character/id/<int:id>', views.character_by_id, name='character'),
]