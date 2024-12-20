# utils.py
import json
import os
import sys
import tkinter as tk
from tkinter import filedialog
from typing import Dict, List
import requests
import urllib.parse

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