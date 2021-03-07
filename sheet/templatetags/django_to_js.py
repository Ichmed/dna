from django.template.defaulttags import register
from django.utils.safestring import mark_safe
from dna.settings import BASE_DIR
import os

@register.filter
def to_js_template(path, target="r", source="data"):
	text = open(os.path.join(BASE_DIR, "sheet", "templates", path)).read()
	return mark_safe(f"var _{target} = \"\";" + parse(text, target=target, source=source)[0])

def parse(block, header="", target="r", source="data"):
	result = ""

	beginning = 0
	end = len(block)

	if header != "":
		type, preamble = parse_header(header)
	else:
		type = ""
		preamble = ""

	while True:
		try:		
			start = block.index("{%", beginning)
			stop = block.index("%}", start) + 2

			if start > beginning:
				result += format_plain(block[beginning:start], target)

			beginning = stop

			# print(result)


			tag = block[start+2:stop-2].strip()
			if tag == "end" + type:
				result += block[beginning:start]
				end = stop
				break

			inner, offset = parse(block[stop:], header=tag)
			result += inner
			beginning += offset
		except ValueError:
			if end > beginning:
				result += format_plain(block[beginning:end], target)
			break
	
	# print("Result:", result)
	# print()

	return preamble + result + ("}\n" if "{" in preamble else "\n"), end

escapes = {
	"\n":  "\\n",
	"\"":  "\\\"",
	"'": "\\'",
}

subs = {
	"{{": "\" +",
	"}}": "+ \"",
	"|cat:": "+",
}

def escape(x):
	for a, b in escapes.items():
		x = x.replace(a, b)
	return x

def substitute(x):
	for a, b in subs.items():
		x = x.replace(a, b)
	return x

def format_plain(s, target="r"):
	return f"_{target} += \"" + substitute(escape(s)) + "\";\n"

def parse_header(header):
	header = header.strip()

	type, *rest = header.split()
	preamble = ""

	if type == "for":
		running, _, source= rest
		preamble = f"for({running}_ in {source}){{ var {running} = {source}[{running}_]; "
	elif type == "if":
		preamble = "if (" + (" ".join(rest)).replace("not", "!") + ") {"
	elif type == "with":
		f, _, t = rest
		preamble = f"{{ var {t} = {substitute(f)};"
	# TODO: self closing tags
	# elif type == "static":
	# 	preamble = "\" + " + " ".join(rest) + " + \""

	return type, preamble
	

if __name__ == "__main__":
	print(parse(
"""
<div class="ability clickbox" onclick="smartlink('ability', '{{ability.base.pk}}')">
<input type="hidden" name="base_id" value="{{ability.base.pk}}">
{% with "symbols/bobble_"|cat:ability.base.skill|cat:".png" as path %}
<div class="icon_align"><img class="icon" src="{% static path %}"></div>
{% endwith %}
<input class="name" name="name" value="{{ability.name}}">
{% if ability.base.actionpoints %} <span class="info cost"> Cost: {{ability.base.actionpoints}}</span>{% endif %}
{% if ability.base.chance %} <span class="info chance">Chance: {{ability.base.chance}}</span>{% endif %}
{% if ability.base.range %} <span class="info range">Range: {{ability.base.range}}</span>{% endif %}
{% if ability.base.manacost %} <span class="info mana" onclick="spend('mana', {{ability.base.manacost}}); event.stopPropagation()">Mana: {{ability.base.manacost}}</span>{% endif %}

<div class="level"><input value="{{ability.level}}" name="level"></div>
</div>
"""
)[0])

