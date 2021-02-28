import re
import sys
from http.server import *
import json


class PatternHandler():
	def __init__(self):
		self.patterns = []

	def add_pattern(self, pattern, handler):
		self.patterns.append((pattern, re.compile(pattern + "(.*)"), handler))
		return self
	
	def init(self):
		self.patterns.sort(key= lambda x: -len(x[0]))
		return self

	def handle(self, url):
		for p in self.patterns:
			res = p[1].match(url)
			if(res):
				return p[2].handle(res.group(1))
				
		return 404, "404".encode()
				
	

class DummyHandler:
	def handle(self, url):
		return 200, url.encode()

class Redirect:
	def __init__(self, target, message=""):
		self.message = message
		self.target = target
	
	def handle(self, url):
		return 308, self.message.encode(), {'Location': self.target}
		
class SheetHandler:
	def handle(self, url):
		
		data = json.load(open('config/attributes.json'))
		
		html = "<html><body>{}</body></html>"
		box = '<div class="{name} container" title={full_name}><span class="{name} label">{name}</span><input class="{name} input"></div>'
		
		html = html.format("\n".join([box.format(name=x, **data['main'][x]) for x in data['main']]))
		
		return 200, html.encode()
		
class Handler(BaseHTTPRequestHandler):
	
	def do_GET(self):		
		_, *path = self.path.split("/")
				
		res = main_handler.handle(self.path)
		if(len(res) == 2):
			code, data = res
			headers ={'Content-type': 'text/html'}
		else:
			code, data, headers = res
		
		self.send_response(code)
		for h in headers:
			self.send_header(h, headers[h])
		self.end_headers()
		self.wfile.write(data)
		
def register_handler(pattern, handler):
	main_handler.add_pattern(pattern, handler)
	print('Registered', type(handler), 'under', pattern)
	
def run(port):
	main_handler.init()
	
	
	with HTTPServer(('', port), Handler) as server:
		print('Running...')
		server.serve_forever()
	
	
main_handler = PatternHandler()

if __name__ == '__main__':
	main_handler = PatternHandler()
	main_handler.add_pattern('/api', DummyHandler())
	main_handler.add_pattern('/soundboard', DummyHandler())
	main_handler.add_pattern('/search', DummyHandler())
	main_handler.add_pattern('/sheet', SheetHandler())
	
	port = 8000
	
	if len(sys.argv) > 1: port = int(sys.argv[1])
	run(port)