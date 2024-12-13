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

    def select_directory(self, label) -> None:
        """
        Prompt the user to select the directory path and update the label.
        """
        self.directory_path = filedialog.askdirectory()
        if self.directory_path:
            label.config(text=f"Selected Directory: {self.directory_path}")

    def select_save_directory(self, label) -> None:
        """
        Prompt the user to select the directory path for saving messages.txt and update the label.
        """
        self.save_directory_path = filedialog.askdirectory()
        if self.save_directory_path:
            label.config(text=f"Save Directory: {self.save_directory_path}")

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
        # Set the window size
        self.root.geometry("600x500")
        self.root.minsize(600, 500)
        self.root.maxsize(600, 500)
        self.root.resizable(False, False)

        # Label and Entry for Discord Username
        tk.Label(self.root, text="Enter your Discord username:").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        # Button to Select Directory
        self.directory_label = tk.Label(self.root, text="Selected Directory: ")
        self.directory_label.pack()
        tk.Button(self.root, text="Select 'package' Directory", command=lambda: self.dump_messages.select_directory(self.directory_label)).pack()

        # Button to Select Save Directory
        self.save_directory_label = tk.Label(self.root, text="Save Directory: ")
        self.save_directory_label.pack()
        tk.Button(self.root, text="Select Save Directory", command=lambda: self.dump_messages.select_save_directory(self.save_directory_label)).pack()

        # Text widget to display console output without vertical scrollbar
        self.console_output = tk.Text(self.root, width=70, height=20, wrap=tk.WORD)
        self.console_output.pack(fill=tk.BOTH, expand=True)

        # Redirect sys.stdout to the Text widget
        class ConsoleRedirector:
            def __init__(self, text_widget):
                self.text_widget = text_widget

            def write(self, message):
                self.text_widget.insert(tk.END, message)
                self.text_widget.see(tk.END)

            def flush(self):
                pass

        self.console_redirector = ConsoleRedirector(self.console_output)
        import sys
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

        tk.Button(self.root, text="Proceed", command=proceed_modal).pack()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = GUI()
    gui.run()
