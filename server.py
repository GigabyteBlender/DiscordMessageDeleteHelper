from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import urllib.parse
import threading
import time
import os
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE

# Global variable to track if the server is running
server_running = False
httpd = None

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
                
                if access_token is None:
                    # Handle failure to retrieve an access token
                    print('Failed to get access token')
                    self.send_error(500, 'Failed to get access token')
                else:
                    # Save user data
                    self.save_user_data(access_token)
                    
                    # Respond with an HTML page indicating successful authorization
                    self.send_response(200)  # Send HTTP 200 OK status
                    self.send_header('Content-type', 'text/html')  # Indicate response type is HTML
                    self.end_headers()
                    self.wfile.write(b'''
                    <html>
                        <head>
                            <title>Authorization Complete</title>
                            <style>
                                body {
                                    font-family: Arial, sans-serif;
                                    background-color: #36393F;
                                    color: #FFFFFF;
                                    display: flex;
                                    justify-content: center;
                                    align-items: center;
                                    height: 100vh;
                                    margin: 0;
                                }
                                .container {
                                    background-color: #2C2F33;
                                    padding: 30px;
                                    border-radius: 8px;
                                    text-align: center;
                                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                                }
                                h1 {
                                    color: #7289DA;
                                    margin-bottom: 20px;
                                }
                                p {
                                    margin-bottom: 20px;
                                }
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <h1>Authorization Complete</h1>
                                <p>You have successfully connected to Discord.</p>
                                <p>You can now close this window and return to the application.</p>
                            </div>
                            <script>
                                // Use window.close only if this is a popup/new window
                                if (window.opener) {
                                    window.close();
                                }
                            </script>
                        </body>
                    </html>
                    ''')
                    
                    # Stop the server after successful authorization
                    threading.Thread(target=self.stop_server).start()
        except Exception as e:
            # Handle parsing or processing errors gracefully
            print(f'Error processing request: {e}')
            self.send_error(500, f'Error processing request: {e}')
    
    def stop_server(self):
        # Give the browser time to receive the response before stopping the server
        time.sleep(1)
        global httpd, server_running
        if httpd:
            server_running = False
            httpd.shutdown()
    
    def save_user_data(self, access_token):
        try:
            # Get user data using the access token
            user_response = requests.get(
                'https://discord.com/api/users/@me',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            user_data = user_response.json()

            with open("data.txt", "w+") as f:
                user_id = user_data.get('id', 'Unknown')
                user_email = user_data.get('email', 'Unknown')
                user_username = user_data.get('username', 'Unknown')
                user_verified = user_data.get('verified', False)
                
                f.write(f'{user_id}\n{user_email}\n{user_username}\n{user_verified}')
                
            print(f"User data saved: {user_username} ({user_email})")
        except Exception as e:
            # Handle JSON parsing errors
            print(f'Error saving user data: {e}')

    # Override log_message to suppress server logs or redirect them
    def log_message(self, format, *args):
        # Customize logging format if needed
        print(f"Server: {format % args}")

# Function to start the HTTP server
def run_server():
    global httpd, server_running
    
    # Don't start if already running
    if server_running:
        print('Server is already running')
        return
    
    print('Starting server on port 8000...')
    server_address = ('', 8000)  # Bind to all available interfaces on port 8000
    
    try:
        # Initialize HTTP server with custom handler
        httpd = HTTPServer(server_address, RequestHandler)
        server_running = True
        
        # Run the server until stop_server is called
        httpd.serve_forever()
        
        print('Server has stopped')
    except Exception as e:
        print(f'Error starting server: {e}')
    finally:
        server_running = False

# Function to check if authentication has completed
def check_auth_status():
    # Check if data.txt exists and contains valid user data
    if os.path.exists("data.txt"):
        try:
            with open("data.txt", "r") as f:
                lines = f.readlines()
                if len(lines) >= 3:
                    return True
        except Exception as e:
            print(f"Error reading auth data: {e}")
    
    return False

# Function to get current authentication status
def get_user_info():
    if os.path.exists("data.txt"):
        try:
            with open("data.txt", "r") as f:
                user_data = [line.strip() for line in f.readlines()]
                if len(user_data) >= 3:
                    return {
                        "id": user_data[0],
                        "email": user_data[1],
                        "username": user_data[2],
                        "verified": user_data[3] if len(user_data) > 3 else "False"
                    }
        except Exception as e:
            print(f"Error reading user data: {e}")
    
    return None

# Function to clear authentication data
def clear_auth_data():
    if os.path.exists("data.txt"):
        try:
            os.remove("data.txt")
            return True
        except Exception as e:
            print(f"Error clearing auth data: {e}")
    
    return False

# Run the server if this script is executed directly
if __name__ == "__main__":
    run_server()