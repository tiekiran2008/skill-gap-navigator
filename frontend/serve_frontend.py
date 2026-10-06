import http.server
import socketserver
import os

PORT = 5173
DIR = r'D:\KAI-LLM\java project\frontend\dist'

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

with socketserver.TCPServer(('', PORT), Handler) as httpd:
    print(f'Frontend serving on http://localhost:{PORT}')
    httpd.serve_forever()
