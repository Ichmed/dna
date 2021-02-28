from PIL import Image, ImageColor


def build_bobble(skill):
		if skill.isPseudo: return
		bobble = Image.open('rulebook/static/symbols/empty_bobble.png')
		result = bobble.copy()
		try:
			result = Image.alpha_composite(result, Image.open('rulebook/static/symbols/' + skill.name + '.png'))
		except FileNotFoundError:
			print('Could not find icon for', skill.name)
			
		r, g, b = ImageColor.getrgb(skill.color)
		
		ld = result.load()
		width, height = result.size
		for y in range(height):
			for x in range(width):
				ld[x,y] = int(r * ld[x,y][0] / 255), int(g * ld[x,y][1] / 255), int(b * ld[x,y][2] / 255), ld[x, y][3]
		
		
		result.save('rulebook/static/symbols/bobble_' + skill.name + '.png')
		print("Updated bobble for", skill.name)
