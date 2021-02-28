import sys, subprocess, os


files = {}

def should_update():
	result = False
	for root, dirs, files in os.walk():
		for name in files:
			p = os.path.join(root, name)
			time = os.path.getmtime(p)
			if not p in files or time < files[p]:
				result = True