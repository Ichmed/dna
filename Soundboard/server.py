import sqlite3
from http.server import *
import urllib
import os, sys


def get_query(query):
	return '["chirp_0.wav", "chirp_1.wav"]'

class Handler(BaseHTTPRequestHandler):
	
	def do_GET(self):
		_, *path = self.path.split("/")
		
		if path[0] == "get":
			query = "/".join(path[1:])
			
			if os.path.isdir(query):
				
				all_files = []
				for root, dirs, files in os.walk(query):
					for file in files:
						all_files.append(root.replace('\\', '/') + "/" + file)
				
				data = ('["' + '","'.join(all_files) + '"]').encode()
				code = 200
			elif os.path.isfile(query):
				data = ('["' + query + '"]').encode()
				code = 200
			else:
				code = 404
				data = "404".encode()
		elif path[0] == "list":
			
			data = ('["' + '","'.join([x for x in os.listdir('.') if os.path.isdir(x) and not x[0] == '_']) + '"]').encode()
			code = 200
		else:
			
			path = "/".join(path)
			
			if not '.' in path: path += ".html"
			
			if(os.path.isfile(path)):
				code = 200
				if path.endswith('.html'):
					data = open(path, 'r').read().encode()
				else:
					data = open(path, 'rb').read()
				
			else:
				code = 404
				data = "404".encode()
				
			
		self.send_response(code)
		#self.send_header('Content-type', mime)
		self.end_headers()
		self.wfile.write(data)

if __name__ == "__main__":
	print('Running...')
	port = 8000
	
	if len(sys.argv) > 1: port = int(sys.argv[1])
	
	with HTTPServer(('', port), Handler) as server:
		server.serve_forever()
