# server.py
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import urllib.parse
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/callback'):
            code = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)['code'][0]
            token_response = requests.post(
                'https://discord.com/api/oauth2/token',
                data={
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'code': code,
                    'grant_type': 'authorization_code',
                    'redirect_uri': REDIRECT_URI,
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            token_data = token_response.json()
            access_token = token_data.get('access_token')
            user_response = requests.get(
                'https://discord.com/api/users/@me',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            user_data = user_response.json()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f'User Data: {user_data}'.encode())

def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, RequestHandler)
    print('Starting httpd on port 8000...')
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()