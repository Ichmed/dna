from django.template.defaulttags import register
from django.utils.safestring import mark_safe

@register.filter
def to_js_template(path, source="data"):
	text = open(path).read()
	return mark_safe("var _R = \"\";" + parse(text, source=source))

def parse(block, header="", source="data"):
	result = ""

	beginning = 0
	end = len(block)

	if header != "":
		type, preamble = parse_header(header)
	else:
		type = ""
		preamble = "{"

	while True:
		try:		
			start = block.index("{%", beginning)
			stop = block.index("%}", start) + 2

			if start > beginning:
				result += format_plain(block[beginning:start])

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
				result += format_plain(block[beginning:end])
			break
	
	# print("Result:", result)
	# print()

	return preamble + result + "}", end

def format_plain(s):
	return "_R += \"" + s.replace("\n", "\\n") + "\";"

def parse_header(header):
	header = header.strip()

	type, *rest = header.split()
	preamble = "{"

	if type == "for":
		running, _, source= rest
		preamble = f"for({running}_ in {source}){{ var {running} = {source}[{running}_]; "
	elif type == "if":
		preamble = "(" + " ".join(rest) + ") {"

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

