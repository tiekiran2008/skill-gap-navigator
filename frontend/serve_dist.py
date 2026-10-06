import http.server
import json
import os
import urllib.request
import urllib.error
from http.server import SimpleHTTPRequestHandler

DIST_DIR = r'D:\KAI-LLM\java project\frontend\dist'
PORT = 5174
BACKEND_URL = 'http://127.0.0.1:8000'


class ProxyHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST_DIR, **kwargs)

    def do_GET(self):
        if self.path.startswith('/api') or self.path.startswith('/health') or self.path.startswith('/careers') or self.path.startswith('/companies') or self.path.startswith('/analyze') or self.path.startswith('/upload-resume') or self.path.startswith('/recommend') or self.path.startswith('/company-analysis'):
            self._proxy_request('GET')
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api') or self.path.startswith('/analyze') or self.path.startswith('/upload-resume') or self.path.startswith('/recommend') or self.path.startswith('/company-analysis'):
            self._proxy_request('POST')
        else:
            self.send_error(404)

    def do_PUT(self):
        if self.path.startswith('/api'):
            self._proxy_request('PUT')
        else:
            self.send_error(404)

    def do_DELETE(self):
        if self.path.startswith('/api'):
            self._proxy_request('DELETE')
        else:
            self.send_error(404)

    def _proxy_request(self, method):
        url = BACKEND_URL + self.path
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        headers = {}
        for key in ['Content-Type', 'Accept', 'Authorization']:
            if self.headers.get(key):
                headers[key] = self.headers.get(key)

        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req) as response:
                resp_body = response.read()
                self.send_response(response.status)
                self.send_header('Content-Type', response.headers.get('Content-Type', 'application/json'))
                self.send_header('Content-Length', str(len(resp_body)))
                self.end_headers()
                self.wfile.write(resp_body)
        except urllib.error.HTTPError as e:
            resp_body = e.read()
            self.send_response(e.code)
            self.send_header('Content-Type', e.headers.get('Content-Type', 'application/json'))
            self.send_header('Content-Length', str(len(resp_body)))
            self.end_headers()
            self.wfile.write(resp_body)
        except Exception as e:
            error_body = json.dumps({"detail": str(e)}).encode()
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(error_body)))
            self.end_headers()
            self.wfile.write(error_body)

    def log_message(self, format, *args):
        pass


os.chdir(DIST_DIR)
httpd = http.server.HTTPServer(("0.0.0.0", PORT), ProxyHandler)
httpd.serve_forever()
