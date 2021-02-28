from django.urls import path

from . import views

urlpatterns = [
	path('editor/<table>', views.editor, name='post'),
	path('editor/<table>/<int:id>', views.editor, name='post'),
	path('edit/<table>/<int:id>', views.post, name='post'),
	path('edit/<table>/None', views.post, name='post'),
	path('search/<table>/<query>', views.search, name='search'),
	path('search/<table>', views.search, name='search'),
	path('delete/<table>/<int:id>', views.delete, name='delete'),
	path('tree/<table>/<int:id>', views.tree, name='tree'),

	path('api/search/<table>/<query>', views.api_search, name='api_search'),
	path('api/list/<table>/<query>', views.api_list, name='api_list'),
	path('api/list/<table>/', views.api_list, name='api_list'),
]