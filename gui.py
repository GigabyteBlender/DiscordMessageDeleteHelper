import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import server
import concurrent.futures
from utils import DumpAllMessages, ConsoleRedirector, serverOpen
import sys
import os

class ModernGUI:
    def __init__(self):
        # Initialize the message dumper and set up the main application window
        self.dump_messages = DumpAllMessages()
        self.s_open = serverOpen()
        self.root = tk.Tk()
        self.dump_messages.root = self.root
        self.root.title("Discord Message Dumper")
        
        # Set theme and style
        self.set_theme()
        
        # Function to center the window on the screen
        def center_window(window, width, height):
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            window.geometry(f"{width}x{height}+{x}+{y}")

        # Set window size and center it
        window_width = 700
        window_height = 700
        center_window(self.root, window_width, window_height)
        
        # Create a notebook for tabbed interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.setup_tab = ttk.Frame(self.notebook)
        self.console_tab = ttk.Frame(self.notebook)
        self.help_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.setup_tab, text="Setup")
        self.notebook.add(self.console_tab, text="Console")
        self.notebook.add(self.help_tab, text="Help")
        
        # Setup the tabs
        self.setup_setup_tab()
        self.setup_console_tab()
        self.setup_help_tab()
        
        # Initialize status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def set_theme(self):
        # Define colors
        self.bg_color = "#2C2F33"  # Discord dark theme
        self.accent_color = "#7289DA"  # Discord blurple
        self.text_color = "#FFFFFF"
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure common styles
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabel', background=self.bg_color, foreground=self.text_color)
        style.configure('TButton', background=self.accent_color, foreground=self.text_color)
        style.configure('TNotebook', background=self.bg_color)
        style.configure('TNotebook.Tab', background=self.bg_color, foreground=self.text_color, padding=[10, 5])
        style.map('TNotebook.Tab', background=[('selected', self.accent_color)])
        
        # Set root window color
        self.root.configure(bg=self.bg_color)
    
    def setup_setup_tab(self):
        # Create a frame to organize widgets with spacing
        main_frame = ttk.Frame(self.setup_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Discord Message Delete Helper", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)
        
        # Section 1: Authentication
        auth_frame = ttk.LabelFrame(main_frame, text="Discord Authentication")
        auth_frame.pack(fill=tk.X, pady=10)
        
        auth_desc = ttk.Label(auth_frame, text="Connect to Discord to access your message data", wraplength=600)
        auth_desc.pack(pady=5)
        
        self.oauth_button = ttk.Button(
            auth_frame, 
            text="Connect to Discord", 
            command=lambda: [
                self.update_status("Connecting to Discord..."),
                threading.Thread(target=self.start_auth).start()
            ]
        )
        self.oauth_button.pack(pady=10)
        
        self.user_info_label = ttk.Label(auth_frame, text="Not connected")
        self.user_info_label.pack(pady=5)
        
        # Section 2: Directory Selection
        dir_frame = ttk.LabelFrame(main_frame, text="Directory Selection")
        dir_frame.pack(fill=tk.X, pady=10)
        
        # Input directory
        input_frame = ttk.Frame(dir_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="Messages Directory:").pack(side=tk.LEFT, padx=5)
        self.directory_path_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.directory_path_var, width=40).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(input_frame, text="Browse", command=self.select_input_directory).pack(side=tk.LEFT, padx=5)
        
        # Output directory
        output_frame = ttk.Frame(dir_frame)
        output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_frame, text="Save Directory:").pack(side=tk.LEFT, padx=5)
        self.save_directory_var = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.save_directory_var, width=40).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="Browse", command=self.select_output_directory).pack(side=tk.LEFT, padx=5)
        
        # Section 3: Options
        options_frame = ttk.LabelFrame(main_frame, text="Options")
        options_frame.pack(fill=tk.X, pady=10)
        
        # Exclude channels
        exclude_frame = ttk.Frame(options_frame)
        exclude_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(exclude_frame, text="Exclude Channel IDs (comma-separated):").pack(side=tk.LEFT, padx=5)
        self.exclude_channels_var = tk.StringVar()
        ttk.Entry(exclude_frame, textvariable=self.exclude_channels_var, width=40).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Process button
        self.process_button = ttk.Button(
            main_frame, 
            text="Generate Message ID List", 
            command=self.process_messages
        )
        self.process_button.pack(pady=20)
    
    def setup_console_tab(self):
        console_frame = ttk.Frame(self.console_tab)
        console_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Console header
        ttk.Label(console_frame, text="Console Output", font=("Helvetica", 12, "bold")).pack(pady=5)
        
        # Console output text widget with scrollbar
        console_subframe = ttk.Frame(console_frame)
        console_subframe.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(console_subframe)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.console_output = tk.Text(console_subframe, width=70, height=20, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        self.console_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.console_output.yview)
        
        # Set text widget colors
        self.console_output.config(bg="#36393F", fg="#FFFFFF", insertbackground="#FFFFFF")
        
        # Button to clear console
        ttk.Button(console_frame, text="Clear Console", command=self.clear_console).pack(pady=10)
        
        # Redirect stdout to the console output area
        self.console_redirector = ConsoleRedirector(self.console_output)
        sys.stdout = self.console_redirector
    
    def setup_help_tab(self):
        help_frame = ttk.Frame(self.help_tab)
        help_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Help content
        ttk.Label(help_frame, text="How to Use", font=("Helvetica", 14, "bold")).pack(pady=10)
        
        help_text = """
1. Click "Connect to Discord" to authenticate with your Discord account.

2. Select the 'messages' directory from your Discord data package.

3. Choose a directory where you want to save the generated message ID list.

4. Optionally, enter channel IDs you want to exclude from processing.

5. Click "Generate Message ID List" to process your messages.

6. The generated list will be saved as "messages.txt" in your selected save directory.

7. Submit this list to Discord Support to request message deletion.
        """
        
        help_textbox = tk.Text(help_frame, height=15, wrap=tk.WORD)
        help_textbox.pack(fill=tk.BOTH, expand=True, pady=10)
        help_textbox.insert(tk.END, help_text)
        help_textbox.config(state=tk.DISABLED, bg="#36393F", fg="#FFFFFF")
        
        # Links frame
        links_frame = ttk.Frame(help_frame)
        links_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(links_frame, text="Useful Links:", font=("Helvetica", 12, "bold")).pack(anchor=tk.W)
        
        link_texts = [
            "Discord Developer Portal",
            "Discord Support",
            "How to Request Data Deletion"
        ]
        
        for link in link_texts:
            link_button = ttk.Button(links_frame, text=link, command=lambda l=link: self.open_link(l))
            link_button.pack(anchor=tk.W, pady=2)
    
    def open_link(self, link_text):
        # Define URLs for each link
        links = {
            "Discord Developer Portal": "https://discord.com/developers/applications/",
            "Discord Support": "https://support.discord.com/",
            "How to Request Data Deletion": "https://support.discord.com/hc/en-us/articles/360004027692"
        }
        
        import webbrowser
        webbrowser.open(links.get(link_text, "https://discord.com"))
    
    def start_auth(self):
        self.s_open.start_server_and_open_auth_url()
        # Check for auth completion after a delay
        self.root.after(2000, self.check_auth_status)
    
    def check_auth_status(self):
        if os.path.exists("data.txt"):
            try:
                with open("data.txt", "r") as f:
                    user_data = [line.strip() for line in f.readlines()]
                    if len(user_data) >= 3:
                        user_id, user_email, user_username = user_data[:3]
                        self.user_info_label.config(text=f"Connected as: {user_username} ({user_email})")
                        self.update_status("Authentication successful")
                        return
            except Exception as e:
                print(f"Error reading auth data: {e}")
        
        # If auth not complete yet, check again after a delay
        self.root.after(2000, self.check_auth_status)
    
    def select_input_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.directory_path_var.set(directory)
            self.dump_messages.directory_path = directory
            self.update_status(f"Selected input directory: {directory}")
    
    def select_output_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.save_directory_var.set(directory)
            self.dump_messages.save_directory_path = directory
            self.update_status(f"Selected output directory: {directory}")
    
    def process_messages(self):
        # Check if all required fields are set
        if not self.dump_messages.directory_path:
            messagebox.showerror("Error", "Please select a messages directory first")
            return
            
        if not self.dump_messages.save_directory_path:
            messagebox.showerror("Error", "Please select a save directory first")
            return
        
        # Set exclude channels
        exclude_channels_str = self.exclude_channels_var.get()
        if exclude_channels_str:
            self.dump_messages.exclude_channels = [channel.strip() for channel in exclude_channels_str.split(',')]
        
        # Switch to console tab
        self.notebook.select(1)
        
        # Process in a separate thread to avoid freezing the GUI
        self.update_status("Processing messages...")
        threading.Thread(target=self.process_messages_thread).start()
    
    def process_messages_thread(self):
        try:
            # Dump messages and save them
            print("Starting to process messages...")
            messages = self.dump_messages.dump_all()
            self.dump_messages.save_messages(messages, self.dump_messages.save_directory_path)
            print(f"Successfully generated message ID list to {os.path.join(self.dump_messages.save_directory_path, 'messages.txt')}")
            
            # Show success message
            self.root.after(0, lambda: messagebox.showinfo("Success", "Message ID list has been generated successfully!"))
            self.update_status("Process completed")
        except Exception as e:
            print(f"An error occurred: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {e}"))
            self.update_status("Process failed")
    
    def clear_console(self):
        self.console_output.delete(1.0, tk.END)
    
    def update_status(self, message):
        self.status_var.set(message)
    
    def run(self):
        # Start the Tkinter event loop
        self.root.mainloop()

if __name__ == "__main__":
    # Run the server in a separate thread to handle requests
    executor = concurrent.futures.ThreadPoolExecutor()
    executor.submit(server.run_server)
    
    # Create and run the GUI application
    gui = ModernGUI()
    gui.run()