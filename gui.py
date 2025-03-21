import tkinter as tk
import threading
import server
import concurrent.futures
from utils import DumpAllMessages, ConsoleRedirector, serverOpen
import sys

class GUI:
    def __init__(self):
        # Initialize the message dumper and set up the main application window
        self.dump_messages = DumpAllMessages()
        self.s_open = serverOpen()
        self.dump_messages.root = self.root = tk.Tk()
        self.root.title("Discord Message Dumper")

        # Function to center the window on the screen
        def center_window(window, width, height):
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            window.geometry(f"{width}x{height}+{x}+{y}")

        # Set window size and center it
        window_width = 650
        window_height = 650
        center_window(self.root, window_width, window_height)

        # Add a button to initialize Discord OAuth process
        tk.Label(self.root, text="Initialize Discord OAuth").pack()
        self.oauth_button = tk.Button(self.root, text="Initialize", command=lambda: [threading.Thread(target=self.s_open.start_server_and_open_auth_url).start()])
        self.oauth_button.pack()
        
        # Add UI elements for selecting input and output directories
        self.directory_label = tk.Label(self.root, text="Selected Directory: ")
        self.directory_label.pack()
        directory_button = tk.Button(self.root, text="Select 'messages' Directory", command=lambda: self.dump_messages.select_directory(self.directory_label, directory_button))
        directory_button.pack()
        
        self.save_directory_label = tk.Label(self.root, text="Save Directory: ")
        self.save_directory_label.pack()
        save_directory_button = tk.Button(self.root, text="Select Save Directory", command=lambda: self.dump_messages.select_save_directory(self.save_directory_label, save_directory_button))
        save_directory_button.pack()

        # Add an entry field for excluding specific channel IDs
        tk.Label(self.root, text="Enter channel IDs to exclude (comma-separated):").pack()
        self.exclude_channels_entry = tk.Entry(self.root)
        self.exclude_channels_entry.pack()
        exclude_channels_button = tk.Button(self.root, text="Set Exclude Channels", command=lambda: self.dump_messages.set_exclude_channels(self.exclude_channels_entry, exclude_channels_button))
        exclude_channels_button.pack()

        # Add a console output area to display logs and messages
        self.console_output = tk.Text(self.root, width=70, height=20, wrap=tk.WORD)
        self.console_output.pack(fill=tk.BOTH, expand=True)

        # Redirect stdout to the console output area
        self.console_redirector = ConsoleRedirector(self.console_output)
        sys.stdout = self.console_redirector

        proceed_button = tk.Button(self.root, text="Proceed", command=proceed_modal)
        proceed_button.pack()

    def run(self) -> None:
        # Start the Tkinter event loop
        self.root.mainloop()
        
# Define the proceed button's behavior to start the main process
def proceed_modal(self):
                
    if self.dump_messages.directory_path and self.dump_messages.save_directory_path:
        self.dump_messages.main(self.console_redirector)
                
        try:
            with open("data.txt", "r") as f:
                user_data = [line.strip() for line in f.readlines()]
                if len(user_data) >= 4:
                    user_id, user_email, user_username, user_verified = user_data[:4]
                    print(f'User ID: {user_id}')
                    print(f'User Email: {user_email}')
                    print(f'User Username: {user_username}')
                    print(f'User Verified: {user_verified}')
                else:
                    print('Incomplete user data')
        except Exception as e:
            print(f'Error reading data: {e}')
    else:  
        print("\nPlease fill in all fields.")

if __name__ == "__main__":
    # Run the server in a separate thread to handle requests
    executor = concurrent.futures.ThreadPoolExecutor()
    executor.submit(server.run_server)
    # Create and run the GUI application
    gui = GUI()
    gui.run()