from PIL import Image, ImageColor


def build_bobble(name, color, no_icon=False):
	try:
		bobble = Image.open('resc/static/symbols/empty_bobble.png')
		result = bobble.copy()
		if not no_icon: result = Image.alpha_composite(result, Image.open('resc/static/symbols/' + name + '.png'))
			
		r, g, b = ImageColor.getrgb(color)
		
		ld = result.load()
		width, height = result.size
		for y in range(height):
			for x in range(width):
				ld[x,y] = int(r * ld[x,y][0] / 255), int(g * ld[x,y][1] / 255), int(b * ld[x,y][2] / 255), ld[x, y][3]
		
		
		result.save('resc/generated/symbols/bobble_' + name + '.png')
	except FileNotFoundError:
		print('Could not find icon for', name)

	
if __name__ == '__main__':
	build_bobble('melee', '#FFFF00')