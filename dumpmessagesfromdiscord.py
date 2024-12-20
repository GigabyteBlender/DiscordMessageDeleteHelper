import json
import os
import sys
import tkinter as tk
from tkinter import filedialog
from typing import Dict, List
import requests
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import webbrowser
import threading

# Replace these with your actual Discord application credentials
CLIENT_ID = '1319665737412907109'
CLIENT_SECRET = '8Sa2WtHUHid_MtgnZnE_TuEh3y7z9xLM'
REDIRECT_URI = 'http://localhost:8000/callback'
SCOPE = 'identify email'  # Corrected scope

# Generate the authorization URL
auth_url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}&response_type=code&scope={urllib.parse.quote(SCOPE)}"

class ConsoleRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)

    def flush(self):
        pass

class DumpAllMessages:
    def __init__(self):
        self.usrName = None
        self.directory_path = None
        self.save_directory_path = None
        self.exclude_channels = []
        self.root = None

    def save_messages(self, messages: Dict[str, List[int]], save_path: str) -> None:
        print('Creating file...')
        file_path = os.path.join(save_path, "messages.txt")
        with open(file_path, "w+") as f:
            for channel_id, message_ids in messages.items():
                if len(channel_id) == 18 and channel_id.isnumeric():
                    if channel_id not in self.exclude_channels:
                        print(f'Saving messages from channel: {channel_id}')
                        f.write(f'{channel_id}:\n\n')
                        f.write(', '.join(map(str, message_ids)))
                        f.write('\n\n')

    def dump_dir(self, path: str) -> List[int]:
        messages = []
        if not os.path.isdir(path):
            return messages
        file_path = f'{path}/messages.json'
        if not os.path.exists(file_path):
            print(f'No messages found in: {path}')
            return messages
        print(f'Dumping messages from: {path}')
        try:
            with open(file_path, 'r', encoding='utf8') as f:
                messages_obj = json.load(f)
                for message in messages_obj:
                    messages.append(message['ID'])
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON in {file_path}: {e}")
            return messages
        return messages

    def dump_all(self) -> Dict[str, List[int]]:
        if not self.directory_path:
            raise ValueError("Directory path not set")
        messages = {}
        for channel in os.listdir(self.directory_path):
            path = os.path.join(self.directory_path, channel)
            channel_id = channel.replace('c', '', 1)
            messages[channel_id] = self.dump_dir(path)
        return messages

    def user_info(self, username: str) -> None:
        self.usrName = username

    def select_directory(self, label, button) -> None:
        self.directory_path = filedialog.askdirectory()
        if self.directory_path:
            label.config(text=f"Selected Directory: {self.directory_path}")
            button.config(bg='#444444', fg='grey')

    def select_save_directory(self, label, button) -> None:
        self.save_directory_path = filedialog.askdirectory()
        if self.save_directory_path:
            label.config(text=f"Save Directory: {self.save_directory_path}")
            button.config(bg='#444444', fg='grey')

    def set_exclude_channels(self, entry, button) -> None:
        exclude_channels_str = entry.get()
        self.exclude_channels = [channel.strip() for channel in exclude_channels_str.split(',')]
        print('excluding channels:\n')
        for channel in self.exclude_channels:
            print(channel)
        button.config(bg='#444444', fg='grey')

    def main(self, console_redirector) -> None:
        try:
            messages = self.dump_all()
            self.save_messages(messages, self.save_directory_path)
            print("Dumped to messages.txt!")
        except Exception as e:
            print(f"An error occurred: {e}")

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

def start_server_and_open_auth_url():
    threading.Thread(target=run_server).start()
    webbrowser.open(auth_url)

class GUI:
    def __init__(self):
        self.dump_messages = DumpAllMessages()
        self.dump_messages.root = self.root = tk.Tk()
        self.root.title("Discord Message Dumper")

        def center_window(window, width, height):
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            window.geometry(f"{width}x{height}+{x}+{y}")

        window_width = 600
        window_height = 600
        center_window(self.root, window_width, window_height)

        tk.Label(self.root, text="Initialize Discord OAuth").pack()
        self.oauth_button = tk.Button(self.root, text="Initialize", command=start_server_and_open_auth_url)
        self.oauth_button.pack()

        self.directory_label = tk.Label(self.root, text="Selected Directory: ")
        self.directory_label.pack()
        directory_button = tk.Button(self.root, text="Select 'messages' Directory", command=lambda: self.dump_messages.select_directory(self.directory_label, directory_button))
        directory_button.pack()

        self.save_directory_label = tk.Label(self.root, text="Save Directory: ")
        self.save_directory_label.pack()
        save_directory_button = tk.Button(self.root, text="Select Save Directory", command=lambda: self.dump_messages.select_save_directory(self.save_directory_label, save_directory_button))
        save_directory_button.pack()

        tk.Label(self.root, text="Enter channel IDs to exclude (comma-separated):").pack()
        self.exclude_channels_entry = tk.Entry(self.root)
        self.exclude_channels_entry.pack()
        exclude_channels_button = tk.Button(self.root, text="Set Exclude Channels", command=lambda: self.dump_messages.set_exclude_channels(self.exclude_channels_entry, exclude_channels_button))
        exclude_channels_button.pack()

        self.console_output = tk.Text(self.root, width=70, height=20, wrap=tk.WORD)
        self.console_output.pack(fill=tk.BOTH, expand=True)

        self.console_redirector = ConsoleRedirector(self.console_output)
        sys.stdout = self.console_redirector

        def proceed_modal():
            if self.dump_messages.directory_path and self.dump_messages.save_directory_path:
                self.dump_messages.main(self.console_redirector)
                print("Process completed. You can now close the window.")
            else:
                print("Please fill in all fields.")

        proceed_button = tk.Button(self.root, text="Proceed", command=proceed_modal)
        proceed_button.pack()

    def run(self) -> None:
        self.root.mainloop()

if __name__ == "__main__":
    gui = GUI()
    gui.run()