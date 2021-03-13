from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import mark_safe
from colorfield.fields import ColorField
from django.db.models import BooleanField, ManyToOneRel, ManyToManyField, ManyToManyRel
from django.forms.models import model_to_dict
from .query import get_model_for_name
from .query import perform_query
from .models import Skill

from django.http import Http404

import json

from igraph import Graph

# Create your views here.def index(request):

def tree(request, table, id):
	# Create tree
	base = get_model_for_name(table).objects.get(id=id)
	net = dict()
	l = [base]
	l_old = {base.id: base}
	while l:
		e = l.pop()
		if not e.id in net: net[e.id] = []
		new = e.required.all()
		for c in new:
			print("Add child", c)
			net[e.id].append(c.id)
			if not c.id in l_old:
				l.append(c)
				l_old[c.id] = c
		new = e.requires.all()
		for p in new:
			print("Add parent", p)
			if not p.id in net: net[p.id] = []
			net[p.id].append(e.id)
			if not p.id in l_old:
				l.append(p)
				l_old[p.id] = p
	
	# Transform tree to conform to stupid vertex index restrictions
	net2 = {}
	for i, e in enumerate(net.keys()):
		net2[e] = (i, net[e])
	
	print(net2)
	# Create Graph
	g = Graph(directed=True)
	g.add_vertices(len(net2))
	for k in net2:
		for c in net2[k][1]:
			g.add_edges([(net2[k][0], net2[c][0])])
	print(g.get_edgelist())
	# Construct Layout
	lay = g.layout_sugiyama(maxiter=100)
	#lay = g.layout_grid_fruchterman_reingold()
	
	# Transform Layout
	#lay.fit_into((200, 100), False)

	lay.fit_into((1, 1), False)
	lay.scale(200)

	print(len(net2))
	print(len(lay.coords))
	# Construct Context for render
	ts = [(l_old[i], lay[net2[i][0]]) for i in l_old]
	edges = [((lay[x][0] + 10, lay[x][1] + 20), (lay[y][0] + 10, lay[y][1])) for x, y in g.get_edgelist()]
	return render(request, "rulebook/tree.html", {"data": ts, "type": table, "edges": edges, "root": base, "mode": "bobble", "skip": False})


def search(request, table, query=None):
	#context = {"abilities": Ability.objects.all()}
	context = {"results": perform_query(table, query), "type": table, "skip": False}
	return render(request, 'rulebook/search.html', context)

def api_search(_, table, query):
	try:
		o = perform_query(table, query)[0]
		d = model_to_dict(o, fields=[field.name for field in o._meta.fields]) #TODO: improve this
		return JsonResponse(d)
	except Exception as e:
		print(e)
		raise Http404("does not exist")

def api_list(request, table, query=None):
	if query is None:
		query = "name:" + request.GET.get('q', '')
	elif 'q' in request.GET:
		query += " + name:" + request.GET.get('q', '')

	print(query)

	return JsonResponse({'results':[{'id': x.id, 'text': x.name} for x in perform_query(table, query, page=request.GET.get('page', -1))]})

def editor(request, table, id=None):
	m = get_model_for_name(table)
	
	if id == None:
		e = m()
	else:
		e = m.objects.get(id=id)
	

	for key in request.GET:
		if key == 'parent_id' and request.GET['parent_id'] != "":
			#print("parent", request.GET['parent_id'])
			e.parent = m.objects.get(id=request.GET['parent_id'])
		elif key == 'skill_id':
			e.skill = Skill.objects.get(id=request.GET['skill_id'])
		else:
			setattr(e, key, request.GET[key])

	context = {}
	for x in m._meta.get_fields(include_hidden=False):
		if type(x) == ManyToOneRel: 
			continue
		#Construct the displayed requires_raw field from the actual requires_raw field and the abilities that are stored as MtM
		#print(x.name)
		if x.name == 'parent' and e.parent:
			context['parent_id'] = e.parent.id
		if x.name == 'id' and e.id:
			context['self_id'] = e.id
		if x.name == 'requires_raw':
			r = []
			for parent in e.requirement.all():
				if parent.requires.name == parent.display:
					r.append(parent.display)
				else:
					r.append(parent.requires.name + "|" + parent.display)
			if e.requires_raw != None: r += e.requires_raw.split('\n')
			e.requires_raw = ";".join(r)

		if table == "ability": 
			if x.name in ["cost", "leveling", "skill"]:
				context[x.name] = getattr(e, x.name)
				continue

		if type(x) in [ManyToManyField, ManyToManyRel] and id == None: continue
		i_type = "textarea"
		if type(x) == ColorField:
			i_type = "color"
		elif type(x) == BooleanField:
			i_type = "checkbox"
		

		if i_type == "textarea": context[x.name] = mark_safe("<textarea placeholder={} name={}>{}</textarea>".format(x.name.replace('_', ' ').capitalize(), x.name, getattr(e, x.name) or ""))
		else: context[x.name] = mark_safe("<input name={} type={} value={}>".format(x.name, i_type, getattr(e, x.name) or ""))
	
	#print(context)
	d = {"data": context, "type": table, "id": id, "skip": True, "isEditor": True, "skills": Skill.objects.all(), "leveling_types": ["None", "Default", "Inc", "Exp"]}
	try:
		template = "rulebook/" + table + "_editor.html"
		return render(request, template, d)
	except Exception:
		template = "rulebook/" + table + ".html"
		return render(request, template, d)

from .templatetags.cache import invalidate

def post(request, table, id=None):
	m = get_model_for_name(table)
	d = dict(request.POST)
	d = {key: d[key][0] for key in d if d[key][0]}
	print(d)
	if "parent" in d:
		d["parent_id"] = m.objects.get(name=d["parent"]).id
		d.pop("parent")
	if "skill" in d:
		d["skill"] = Skill.objects.get(name=d["skill"])
	#if(id != None):
		# m.objects.filter(id=id).update(**d)
		# e = m.objects.get(id=id)
		# print("Updated")
	#else:
	e = m(**d)
	#	print("Created")

	print(d)
	if "parent_id" in d and d["parent_id"]:
		e.parent = m.objects.get(id=d["parent_id"])
		invalidate("data:" + table + ":" + str(e.parent.id))
	e.save()
	print(e, e.id)
	invalidate("data:" + table + ":" + str(e.id))
	return render(request, 'rulebook/' + table + '.html', {"data": m.objects.get(id=e.id), "type": table, "skip": False})

from datetime import datetime

def delete(request, table, id):
	get_model_for_name(table).objects.filter(id=id).update(DELETED=str(datetime.now()))
	return HttpResponse()