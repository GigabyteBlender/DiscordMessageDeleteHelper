from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import urllib.parse
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

# Custom request handler to handle HTTP requests for the OAuth callback
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Check if the incoming request is for the OAuth callback endpoint
            if self.path.startswith('/callback'):
                
                # Extract the authorization code from the query parameters
                code = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)['code'][0]
                
                # Exchange the authorization code for an access token
                token_response = requests.post(
                    'https://discord.com/api/oauth2/token',
                    data={
                        'client_id': CLIENT_ID,  # Discord client ID
                        'client_secret': CLIENT_SECRET,  # Discord client secret
                        'code': code,  # Authorization code received from Discord
                        'grant_type': 'authorization_code',  # Grant type for OAuth
                        'redirect_uri': REDIRECT_URI,  # Redirect URI registered with Discord
                    },
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
                token_data = token_response.json()
                access_token = token_data.get('access_token')  # Retrieve the access token
                
                if access_token == None:
                    # Handle failure to retrieve an access token
                    SystemError ('Failed to get access token')
                else:               
                    print(f"Access Token: {access_token}")  # Print the access token to console

                    # Fetch the authenticated user's details from Discord
                    user_response = requests.get(
                        'https://discord.com/api/users/@me',
                        headers={'Authorization': f'Bearer {access_token}'}
                    )
                    user_data = user_response.json()

                    # Respond with an HTML page indicating successful authorization
                    self.send_response(200)  # Send HTTP 200 OK status
                    self.send_header('Content-type', 'text/html')  # Indicate response type is HTML
                    self.end_headers()
                    self.wfile.write(b'''
                    <html>
                        <head>
                            <title>Authorization Complete</title>
                        </head>
                        <body>
                            <h1>
                                Authorization Complete. You can now close this window.
                            </h1>
                        </body>
                        <script>
                            JavaScript:window.close()
                        </script>
                    </html>
                    ''')    
        except:
            # Handle parsing or processing errors gracefully
            print('Could not parse request')       

# Function to start the HTTP server
def run_server():
    print('Starting httpd on port 8000...')
    server_address = ('', 8000)  # Bind to all available interfaces on port 8000
    httpd = HTTPServer(server_address, RequestHandler)  # Initialize HTTP server with custom handler
    httpd.serve_forever()  # Run the server indefinitely

# Run the server if this script is executed directly
if __name__ == "__main__":
    run_server()