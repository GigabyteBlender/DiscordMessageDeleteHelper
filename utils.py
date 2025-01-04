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

    # Saves messages to a text file
    def save_messages(self, messages: Dict[str, List[int]], save_path: str) -> None:
        print('Saving messages to messages.txt')
        file_path = os.path.join(save_path, "messages.txt")
        with open(file_path, "w+") as f:
            for channel_id, message_ids in messages.items():
                # Only process valid numeric Discord channel IDs
                if len(channel_id) == 18 and channel_id.isnumeric():
                    if channel_id not in self.exclude_channels:
                        f.write(f'{channel_id}:\n\n')  # Write channel ID
                        f.write(', '.join(map(str, message_ids)))  # Write message IDs
                        f.write('\n\n')

    # Dumps message IDs from a specific directory
    def dump_dir(self, path: str) -> List[int]:
        messages = []
        if not os.path.isdir(path):  # Check if path is valid
            return messages
        file_path = f'{path}/messages.json'
        if not os.path.exists(file_path):  # Check if messages.json exists
            print(f'No messages found in: {path}')
            return messages
        try:
            with open(file_path, 'r', encoding='utf8') as f:
                messages_obj = json.load(f)
                for message in messages_obj:
                    messages.append(message['ID'])  # Collect message IDs
        except json.JSONDecodeError as e:
            # Handle JSON parsing errors
            print(f"Error parsing JSON in {file_path}: {e}")
            return messages
        return messages

    # Dumps messages from all directories
    def dump_all(self) -> Dict[str, List[int]]:
        if not self.directory_path:
            # Raise an error if directory is not set
            raise ValueError("Directory path not set")
        messages = {}
        # Iterate through all subdirectories (channels) in the directory path
        for channel in os.listdir(self.directory_path):
            path = os.path.join(self.directory_path, channel)
            # Remove the prefix (if any) from the channel name
            channel_id = channel.replace('c', '', 1)
            messages[channel_id] = self.dump_dir(path)
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
        self.exclude_channels = [channel.strip() for channel in exclude_channels_str.split(',')]
        print('excluding channels:\n')
        for channel in self.exclude_channels:
            print(channel)
        # Update the button appearance
        button.config(bg='#444444', fg='grey')

    # Main function to handle the complete dumping process
    def main(self, console_redirector) -> None:
        try:
            # Dump messages and save them
            print("Sorting through messages...")
            messages = self.dump_all()
            self.save_messages(messages, self.save_directory_path)
            print("Succesfully dumped to messages.txt\n")
        except Exception as e:
            # Handle unexpected errors
            print(f"An error occurred: {e}")
            
class serverOpen:
    def start_server_and_open_auth_url(self):
            # Construct the Discord OAuth URL and open it in the web browser
            auth_url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPE}"
            webbrowser.open(auth_url)