import tkinter as tk
from tkinter import filedialog
import webbrowser
import threading
from utils import DumpAllMessages, ConsoleRedirector
from config import CLIENT_ID, REDIRECT_URI, SCOPE
import urllib.parse
import sys
import os

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

        auth_url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}&response_type=code&scope={urllib.parse.quote(SCOPE)}"

        tk.Label(self.root, text="Initialize Discord OAuth").pack()
        self.oauth_button = tk.Button(self.root, text="Initialize", command=lambda: [threading.Thread(target=self.start_server_and_open_auth_url).start()])
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

    def start_server_and_open_auth_url(self):
        os.system("python server.py &")
        auth_url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}&response_type=code&scope={urllib.parse.quote(SCOPE)}"
        webbrowser.open(auth_url)

    def run(self) -> None:
        self.root.mainloop()

if __name__ == "__main__":
    gui = GUI()
    gui.run()