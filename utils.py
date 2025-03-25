import json
import os
import tkinter as tk
from tkinter import filedialog
from typing import Dict, List
import webbrowser
from config import CLIENT_ID, REDIRECT_URI, SCOPE

# Redirects console output to a Tkinter text widget
class ConsoleRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        # Insert a message into the text widget
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)

    def flush(self):
        # Method is required for compatibility but does nothing
        pass

# Class to manage dumping messages and directory interactions
class DumpAllMessages:
    def __init__(self):
        self.usrName = None  # Stores user info
        self.directory_path = None  # Path to the directory containing messages
        self.save_directory_path = None  # Path to save the dumped messages
        self.exclude_channels = []  # List of channels to exclude
        self.root = None  # Tkinter root for GUI integration
        self.progress_callback = None  # Callback to update progress
        self.total_channels = 0
        self.processed_channels = 0
        self.total_messages = 0

    # Register a progress callback function
    def register_progress_callback(self, callback):
        self.progress_callback = callback

    # Update progress and call the callback if registered
    def update_progress(self, message, percent=None):
        if self.progress_callback:
            self.progress_callback(message, percent)
        print(message)

    # Saves messages to a text file
    def save_messages(self, messages: Dict[str, List[int]], save_path: str) -> None:
        self.update_progress('Saving messages to messages.txt')
        file_path = os.path.join(save_path, "messages.txt")
        
        try:
            with open(file_path, "w") as f:
                for channel_id, message_ids in messages.items():
                    # Only process valid numeric Discord channel IDs
                    if len(channel_id) == 18 and channel_id.isnumeric():
                        if channel_id not in self.exclude_channels:
                            f.write(f'{channel_id}:\n\n')  # Write channel ID
                            f.write(', '.join(map(str, message_ids)))  # Write message IDs
                            f.write('\n\n')
                            
            self.update_progress(f'Successfully saved {self.total_messages} message IDs from {len(messages)} channels')
        except Exception as e:
            raise IOError(f"Failed to save messages: {e}")

    # Dumps message IDs from a specific directory
    def dump_dir(self, path: str) -> List[int]:
        messages = []
        if not os.path.isdir(path):  # Check if path is valid
            return messages
            
        file_path = f'{path}/messages.json'
        if not os.path.exists(file_path):  # Check if messages.json exists
            self.update_progress(f'No messages found in: {path}')
            return messages
            
        try:
            with open(file_path, 'r', encoding='utf8') as f:
                messages_obj = json.load(f)
                for message in messages_obj:
                    messages.append(message['ID'])  # Collect message IDs
                    
            self.total_messages += len(messages)
            self.update_progress(f'Found {len(messages)} messages in {os.path.basename(path)}')
        except json.JSONDecodeError as e:
            # Handle JSON parsing errors
            self.update_progress(f"Error parsing JSON in {file_path}: {e}")
            return messages
        except Exception as e:
            self.update_progress(f"Error reading {file_path}: {e}")
            return messages
            
        return messages

    # Dumps messages from all directories
    def dump_all(self) -> Dict[str, List[int]]:
        if not self.directory_path:
            # Raise an error if directory is not set
            raise ValueError("Directory path not set")
            
        messages = {}
        self.total_messages = 0
        
        # Count total channels first for progress reporting
        try:
            channel_dirs = [d for d in os.listdir(self.directory_path) 
                           if os.path.isdir(os.path.join(self.directory_path, d))]
            self.total_channels = len(channel_dirs)
            self.processed_channels = 0
            
            self.update_progress(f"Found {self.total_channels} channels to process")
            
            # Iterate through all subdirectories (channels) in the directory path
            for channel in channel_dirs:
                path = os.path.join(self.directory_path, channel)
                # Remove the prefix (if any) from the channel name
                channel_id = channel.replace('c', '', 1)
                
                # Skip excluded channels
                if channel_id in self.exclude_channels:
                    self.update_progress(f"Skipping excluded channel: {channel_id}")
                    continue
                    
                self.update_progress(f"Processing channel: {channel_id}", 
                                    percent=int(100 * self.processed_channels / self.total_channels))
                
                messages[channel_id] = self.dump_dir(path)
                self.processed_channels += 1
                
            self.update_progress("Processing complete", 100)
        except Exception as e:
            raise RuntimeError(f"Failed to process messages: {e}")
            
        return messages

    # Sets user information
    def user_info(self, username: str) -> None:
        self.usrName = username

    # Opens a dialog to select the directory containing messages
    def select_directory(self, label, button) -> None:
        self.directory_path = filedialog.askdirectory()
        if self.directory_path:
            # Update the label and button appearance
            label.config(text=f"Selected Directory: {self.directory_path}")
            button.config(bg='#444444', fg='grey')

    # Opens a dialog to select the directory where messages will be saved
    def select_save_directory(self, label, button) -> None:
        self.save_directory_path = filedialog.askdirectory()
        if self.save_directory_path:
            # Update the label and button appearance
            label.config(text=f"Save Directory: {self.save_directory_path}")
            button.config(bg='#444444', fg='grey')

    # Sets channels to exclude based on user input
    def set_exclude_channels(self, entry, button) -> None:
        exclude_channels_str = entry.get()
        # Parse and clean up channel IDs from user input
        self.exclude_channels = [channel.strip() for channel in exclude_channels_str.split(',') if channel.strip()]
        self.update_progress('Excluding channels:')
        for channel in self.exclude_channels:
            self.update_progress(f"- {channel}")
        # Update the button appearance
        button.config(bg='#444444', fg='grey')

    # Main function to handle the complete dumping process
    def main(self, console_redirector=None) -> None:
        self.console_redirector = console_redirector
        
        try:
            # Dump messages and save them
            self.update_progress("Starting message processing...")
            messages = self.dump_all()
            self.save_messages(messages, self.save_directory_path)
            self.update_progress("Successfully dumped to messages.txt\n")
            return True
        except Exception as e:
            # Handle unexpected errors
            self.update_progress(f"An error occurred: {e}")
            return False
            
class serverOpen:
    def __init__(self):
        self.auth_completed = False
    
    def start_server_and_open_auth_url(self):
        # Construct the Discord OAuth URL and open it in the web browser
        auth_url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPE}"
        try:
            webbrowser.open(auth_url)
            print("Opening Discord authentication in your browser...")
        except Exception as e:
            print(f"Failed to open browser: {e}")
            print(f"Please open this URL manually: {auth_url}")
            
    def is_auth_completed(self):
        # Check if data.txt exists to determine if authentication is complete
        if os.path.exists("data.txt"):
            with open("data.txt", "r") as f:
                lines = f.readlines()
                if len(lines) >= 3:  # At least user_id, email, and username
                    self.auth_completed = True
                    return True
        return False

# Email generation utility
class EmailGenerator:
    def __init__(self):
        self.user_data = None
        self.message_count = 0
        
    def load_user_data(self):
        try:
            with open("data.txt", "r") as f:
                lines = f.readlines()
                if len(lines) >= 3:
                    self.user_data = {
                        "id": lines[0].strip(),
                        "email": lines[1].strip(),
                        "username": lines[2].strip()
                    }
                    return True
                return False
        except Exception:
            return False
    
    def generate_email_template(self, save_path, message_count):
        if not self.load_user_data():
            return "Could not load user data. Please authenticate first."
            
        template = f"""Subject: Request for Message Deletion

To Discord Support Team,

I am writing to request the deletion of my message data as per my rights under data protection regulations.

User Information:
- Discord Username: {self.user_data['username']}
- User ID: {self.user_data['id']}
- Email: {self.user_data['email']}

I have attached a file containing {message_count} message IDs that I would like to be deleted from your servers. These messages are organized by channel ID for your convenience.

Thank you for your assistance with this matter.

Sincerely,
{self.user_data['username']}
"""
        
        try:
            email_path = os.path.join(save_path, "deletion_request_email.txt")
            with open(email_path, "w") as f:
                f.write(template)
            return f"Email template saved to {email_path}"
        except Exception as e:
            return f"Failed to save email template: {e}"