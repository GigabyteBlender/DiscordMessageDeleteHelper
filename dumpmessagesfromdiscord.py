import json
import os
import sys
import tkinter as tk
from tkinter import filedialog, scrolledtext
from typing import Dict, List

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
        """
        Save the messages to a file.

        :param messages: A dictionary where keys are channel IDs and values are lists of message IDs.
        :param save_path: The path where the messages.txt file will be saved.
        """
        print('Creating file...')
        file_path = os.path.join(save_path, "messages.txt")
        with open(file_path, "w+") as f:
            for channel_id, message_ids in messages.items():
                if channel_id not in self.exclude_channels:
                    print(f'Saving messages from channel: {channel_id}')
                    f.write(f'{channel_id}:\n\n')
                    f.write(', '.join(map(str, message_ids)))
                    f.write('\n\n')

    def dump_dir(self, path: str) -> List[int]:
        """
        Dump message IDs from a directory.

        :param path: The path to the directory containing the messages.json file.
        :return: A list of message IDs.
        """
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

    def dump_all(self) -> Dict[str, List[int]]:
        """
        Dump all messages from the messages directory.

        :return: A dictionary where keys are channel IDs and values are lists of message IDs.
        """
        if not self.directory_path:
            raise ValueError("Directory path not set")

        messages = {}
        for channel in os.listdir(self.directory_path):
            path = os.path.join(self.directory_path, channel)
            channel_id = channel.replace('c', '', 1)
            messages[channel_id] = self.dump_dir(path)

        return messages

    def user_info(self, username: str) -> None:
        """
        Set the Discord username.

        :param username: The Discord username.
        """
        self.usrName = username

    def select_directory(self, label, button) -> None:
        """
        Prompt the user to select the directory path and update the label.
        """
        self.directory_path = filedialog.askdirectory()
        if self.directory_path:
            label.config(text=f"Selected Directory: {self.directory_path}")
            button.config(bg='#666666', fg='grey')  # Change button color to dark gray with white text

    def select_save_directory(self, label, button) -> None:
        """
        Prompt the user to select the directory path for saving messages.txt and update the label.
        """
        self.save_directory_path = filedialog.askdirectory()
        if self.save_directory_path:
            label.config(text=f"Save Directory: {self.save_directory_path}")
            button.config(bg='#666666', fg='grey')  # Change button color to dark gray with white text

    def set_exclude_channels(self, entry, button) -> None:
        """
        Set the list of channel IDs to exclude from the output.
        """
        exclude_channels_str = entry.get()
        self.exclude_channels = [channel.strip() for channel in exclude_channels_str.split(',')]
        print('excluding channels:\n')
        for channel in self.exclude_channels:
            print(channel)
        button.config(bg='#666666', fg='grey')  # Change button color to dark gray with white text

    def main(self, console_redirector) -> None:
        """
        Main entry point of the script.
        """
        try:
            messages = self.dump_all()
            self.save_messages(messages, self.save_directory_path)
            print("Dumped to messages.txt!")
        except Exception as e:
            print(f"An error occurred: {e}")

class GUI:
    def __init__(self):
        self.dump_messages = DumpAllMessages()
        self.dump_messages.root = self.root = tk.Tk()
        self.root.title("Discord Message Dumper")

        # Function to center the window
        def center_window(window, width, height):
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            window.geometry(f"{width}x{height}+{x}+{y}")

        # Set the window size
        window_width = 600
        window_height = 600
        center_window(self.root, window_width, window_height)

        # Label and Entry for Discord Username
        tk.Label(self.root, text="Enter your Discord username:").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        # Button to Select Directory
        self.directory_label = tk.Label(self.root, text="Selected Directory: ")
        self.directory_label.pack()
        directory_button = tk.Button(self.root, text="Select 'package' Directory", command=lambda: self.dump_messages.select_directory(self.directory_label, directory_button))
        directory_button.pack()

        # Button to Select Save Directory
        self.save_directory_label = tk.Label(self.root, text="Save Directory: ")
        self.save_directory_label.pack()
        save_directory_button = tk.Button(self.root, text="Select Save Directory", command=lambda: self.dump_messages.select_save_directory(self.save_directory_label, save_directory_button))
        save_directory_button.pack()

        # Label and Entry for Exclude Channels
        tk.Label(self.root, text="Enter channel IDs to exclude (comma-separated):").pack()
        self.exclude_channels_entry = tk.Entry(self.root)
        self.exclude_channels_entry.pack()
        exclude_channels_button = tk.Button(self.root, text="Set Exclude Channels", command=lambda: self.dump_messages.set_exclude_channels(self.exclude_channels_entry, exclude_channels_button))
        exclude_channels_button.pack()

        # Text widget to display console output without vertical scrollbar
        self.console_output = tk.Text(self.root, width=70, height=20, wrap=tk.WORD)
        self.console_output.pack(fill=tk.BOTH, expand=True)

        # Redirect sys.stdout to the Text widget
        self.console_redirector = ConsoleRedirector(self.console_output)
        sys.stdout = self.console_redirector

        # Button to Proceed with modal behavior
        def proceed_modal():
            username = self.username_entry.get()
            if username and self.dump_messages.directory_path and self.dump_messages.save_directory_path:
                self.dump_messages.user_info(username)
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
