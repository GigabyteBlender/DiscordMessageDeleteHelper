import sys
import os
import concurrent.futures
import webbrowser

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QLabel, QPushButton, QLineEdit, QFileDialog,
    QTextEdit, QMessageBox, QStatusBar, QFormLayout, QGroupBox
)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject

import server
import utils

class ConsoleSignals(QObject):
    write_signal = pyqtSignal(str)
    
class ConsoleRedirector:
    def __init__(self, text_widget: QTextEdit):
        self.text_widget = text_widget
        self.signals = ConsoleSignals()
        self.signals.write_signal.connect(self.safe_append)

    def write(self, message):
        # Emit signal instead of directly modifying the widget
        self.signals.write_signal.emit(message)

    def safe_append(self, message):
        # Safely append text to the widget
        if not message.strip():  # Ignore empty messages
            return
        self.text_widget.append(message)
        self.text_widget.verticalScrollBar().setValue(
            self.text_widget.verticalScrollBar().maximum()
        )

    def flush(self):
        pass

class AuthThread(QThread):
    auth_complete = pyqtSignal(dict)
    status_update = pyqtSignal(str)

    def run(self):
        self.status_update.emit("Connecting to Discord...")
        s_open = utils.serverOpen()
        s_open.start_server_and_open_auth_url()
        
        while not s_open.is_auth_completed():
            self.msleep(1000)
        
        try:
            with open("data.txt", "r") as f:
                lines = f.readlines()
                if len(lines) >= 3:
                    user_data = {
                        "id": lines[0].strip(),
                        "email": lines[1].strip(),
                        "username": lines[2].strip()
                    }
                    self.auth_complete.emit(user_data)
                    self.status_update.emit("Authentication successful")
        except Exception as e:
            self.status_update.emit(f"Authentication error: {e}")

class MessageProcessThread(QThread):
    process_complete = pyqtSignal(bool, str)
    message_update = pyqtSignal(str)

    def __init__(self, dump_messages):
        super().__init__()
        self.dump_messages = dump_messages

    def run(self):
        try:
            self.message_update.emit("Starting to process messages...")
            messages = self.dump_messages.dump_all()
            self.dump_messages.save_messages(messages, self.dump_messages.save_directory_path)
            save_path = os.path.join(self.dump_messages.save_directory_path, 'messages.txt')
            self.process_complete.emit(True, f"Successfully generated message ID list to {save_path}")
        except Exception as e:
            self.process_complete.emit(False, f"An error occurred: {e}")
            
class DiscordMessageDumperGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Discord Message Dumper")
        self.resize(600, 600)  # Increased initial window size
        
        # Initialize core components
        self.dump_messages = utils.DumpAllMessages()
        self.s_open = utils.serverOpen()

        # Central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        self.setCentralWidget(central_widget)

        # Tabbed interface with full-width tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabBar::tab {
                width: 201px;  /* Makes tabs fill equally */
                height: 30px;  /* Slightly taller tabs */
            }
        """)
        main_layout.addWidget(self.tab_widget)

        # Create tabs
        self.setup_setup_tab()
        self.setup_console_tab()
        self.setup_help_tab()

        # Status bar
        self.statusBar = QStatusBar()
        main_layout.addWidget(self.statusBar)
        self.setStatusBar(self.statusBar)
        self.update_status("Ready")

        # Set dark theme
        self.set_dark_theme()

    def set_dark_theme(self):
        # Dark color palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)

        self.setPalette(palette)
        self.setStyleSheet("""
            QWidget {
                background-color: #2C2F33;
                color: white;
                font-size: 10pt;
            }
            QGroupBox {
                border: 1px solid #7289DA;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QTabWidget::pane {
                border: 1px solid #7289DA;
            }
            QTabBar::tab {
                background-color: #23272A;
                color: white;
                padding: 5px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #7289DA;
                color: white;
            }
            QPushButton {
                background-color: #7289DA;
                color: white;
                border: none;
                padding: 5px 10px;
                min-height: 25px;
                border-radius: 8px;  /* This adds rounded corners */
            }
            QPushButton:hover {
                background-color: #5b6eae;
            }
            QLineEdit, QTextEdit {
                background-color: #36393F;
                color: white;
                border: 1px solid #23272A;
                padding: 5px;
            }
        """)

    def setup_setup_tab(self):
        setup_tab = QWidget()
        setup_layout = QVBoxLayout(setup_tab)
        setup_layout.setSpacing(10)

        # Authentication Group
        auth_group = QGroupBox("Discord Authentication")
        auth_layout = QVBoxLayout(auth_group)
        
        self.oauth_button = QPushButton("Connect to Discord")
        self.oauth_button.clicked.connect(self.start_auth)
        self.user_info_label = QLabel("Not connected")
        self.user_info_label.setAlignment(Qt.AlignCenter)
        
        auth_layout.addWidget(self.oauth_button)
        auth_layout.addWidget(self.user_info_label)
        setup_layout.addWidget(auth_group)

        # Directories Group
        dir_group = QGroupBox("Directories")
        dir_layout = QFormLayout(dir_group)
        dir_layout.setSpacing(10)

        # Input Directory
        input_row = QHBoxLayout()
        self.input_directory_edit = QLineEdit()
        # Set a minimum width that's about twice the default
        self.input_directory_edit.setMinimumWidth(400)  
        input_browse_button = QPushButton("Browse")
        input_browse_button.clicked.connect(self.select_input_directory)
        
        input_row.addWidget(self.input_directory_edit)
        input_row.addWidget(input_browse_button)
        dir_layout.addRow("Messages Directory:", input_row)

        # Output Directory
        output_row = QHBoxLayout()
        self.output_directory_edit = QLineEdit()
        # Set a minimum width that's about twice the default
        self.output_directory_edit.setMinimumWidth(400)  
        output_browse_button = QPushButton("Browse")
        output_browse_button.clicked.connect(self.select_output_directory)
        
        output_row.addWidget(self.output_directory_edit)
        output_row.addWidget(output_browse_button)
        dir_layout.addRow("Save Directory:", output_row)

        # Exclude Channels
        self.exclude_channels_edit = QLineEdit()
        # Set a minimum width that's about twice the default
        self.exclude_channels_edit.setMinimumWidth(400)  
        dir_layout.addRow("Exclude Channel IDs:", self.exclude_channels_edit)

        setup_layout.addWidget(dir_group)

        # Process Button
        self.process_button = QPushButton("Generate Message ID List")
        self.process_button.clicked.connect(self.process_messages)
        setup_layout.addWidget(self.process_button)

        # Add some stretch to push everything to the top
        setup_layout.addStretch(1)

        # Add tab
        self.tab_widget.addTab(setup_tab, "Setup")
        
    def start_auth(self):
        self.auth_thread = AuthThread()
        self.auth_thread.auth_complete.connect(self.handle_auth_complete)
        self.auth_thread.status_update.connect(self.update_status)
        self.auth_thread.start()

    def handle_auth_complete(self, user_data):
        self.user_info_label.setText(f"Connected as: {user_data['username']} ({user_data['email']})")
        self.oauth_button.setEnabled(False)

    def select_input_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        if directory:
            self.input_directory_edit.setText(directory)
            self.dump_messages.directory_path = directory
            self.update_status(f"Selected input directory: {directory}")

    def select_output_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_directory_edit.setText(directory)
            self.dump_messages.save_directory_path = directory
            self.update_status(f"Selected output directory: {directory}")

    def process_messages(self):
        # Validate directories
        if not self.dump_messages.directory_path:
            QMessageBox.critical(self, "Error", "Please select a messages directory first")
            return
            
        if not self.dump_messages.save_directory_path:
            QMessageBox.critical(self, "Error", "Please select a save directory first")
            return
        
        # Set exclude channels
        exclude_channels_str = self.exclude_channels_edit.text()
        if exclude_channels_str:
            self.dump_messages.exclude_channels = [channel.strip() for channel in exclude_channels_str.split(',')]
        
        # Switch to console tab
        self.tab_widget.setCurrentIndex(1)
        
        # Start processing in a thread
        self.process_thread = MessageProcessThread(self.dump_messages)
        self.process_thread.process_complete.connect(self.handle_process_complete)
        self.process_thread.message_update.connect(print)
        self.process_thread.start()

    def handle_process_complete(self, success, message):
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)

    def clear_console(self):
        self.console_output.clear()

    def update_status(self, message):
        self.statusBar.showMessage(message)

    def setup_console_tab(self):
        console_tab = QWidget()
        console_layout = QVBoxLayout(console_tab)
        console_layout.setSpacing(10)

        # Console Output
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet("""
            background-color: #36393F;
            color: white;
        """)
        console_layout.addWidget(self.console_output)

        # Clear Console Button
        clear_button = QPushButton("Clear Console")
        clear_button.clicked.connect(self.clear_console)
        console_layout.addWidget(clear_button)

        # Redirect stdout
        sys.stdout = ConsoleRedirector(self.console_output)

        self.tab_widget.addTab(console_tab, "Console")

    def setup_help_tab(self):
        help_tab = QWidget()
        help_layout = QVBoxLayout(help_tab)
        help_layout.setSpacing(10)

        # Help Text
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <h2 style='color: #7289DA;'>Discord Message Delete Helper</h2>
        <p>Follow these steps to generate a list of message IDs for deletion:</p>
        <ol>
            <li>Click "Connect to Discord" to authenticate</li>
            <li>Select your Discord messages directory</li>
            <li>Choose a save directory for the message ID list</li>
            <li>Optionally exclude specific channel IDs</li>
            <li>Click "Generate Message ID List"</li>
        </ol>
        <p><strong>Note:</strong> The generated list can be submitted to Discord Support for message deletion.</p>
        """)
        help_layout.addWidget(help_text)

        # Links Group
        links_group = QGroupBox("Useful Links")
        links_layout = QVBoxLayout(links_group)

        link_texts = [
            ("Discord Developer Portal", "https://discord.com/developers/applications/"),
            ("Discord Support", "https://support.discord.com/"),
            ("Data Deletion Request", "https://support.discord.com/hc/en-us/articles/360004027692")
        ]

        for link_text, url in link_texts:
            link_button = QPushButton(link_text)
            link_button.clicked.connect(lambda checked, u=url: webbrowser.open(u))
            links_layout.addWidget(link_button)

        help_layout.addWidget(links_group)
        help_layout.addStretch(1)

        self.tab_widget.addTab(help_tab, "Help")

    # ... (rest of the methods remain the same as in the previous version)

def main():
    # Run the server in a separate thread
    executor = concurrent.futures.ThreadPoolExecutor()
    executor.submit(server.run_server)
    
    # Create and run the GUI application
    app = QApplication(sys.argv)
    gui = DiscordMessageDumperGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()