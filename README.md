# Discord Message Delete Helper

Discord Message Delete Helper is a Python application designed to assist users in generating a list of Discord message IDs. This list can then be used to request the deletion of those messages from Discord support.

## Why was this made?

Discord's approach to message deletion has been a source of frustration for many users. The platform currently does not provide an official method for bulk deleting messages, which has led to the development of this tool.

### Reasons Behind This Decision

- **Preserving Context:** Discord claims that retaining messages is necessary to maintain context in conversations, especially for collaborative projects or communities that rely on historical information.
- **Technical Limitations:** Mass deletion of messages can put a significant strain on Discord's database, which led to the removal of bulk deletion features in the past.
- **Privacy and Security Concerns:** Discord's privacy policy prevents them from reviewing message content without cause, which complicates the process of verifying requests for mass deletion.
- **Compliance with Regulations:** Discord must balance user requests with legal requirements like GDPR's Right to Erasure, which has led to changes in how they handle deletion requests.

### Discord's Measures

To address these issues while still providing some level of control to users, Discord has implemented the following measures:
- Allowing users to request their data package and submit message IDs for deletion.
- Deleting messages on both sides in private DMs but retaining placeholders in server or group chats.
- Gradually adapting their approach to GDPR compliance has affected how deletion requests are processed.

These measures, however, are often seen as inadequate by users who desire more control over their message history. The lack of an official bulk deletion feature has led to the creation of unofficial tools.

In response to this demand, some users have developed methods to generate lists of message IDs from the data provided by Discord, which can then be submitted for deletion. This approach aims to provide users with more control over their message history.

## Features

- **Discord OAuth2 Authentication:** Securely connect to your Discord account
- **Message ID List Generation:** Compile a comprehensive list of message IDs for deletion
- **User-Friendly GUI:** Intuitive interface with multiple tabs for setup, console output, and help
- **Customizable Message Dumping:** 
  - Select specific message directories
  - Exclude specific channel IDs
  - Save message ID list to a chosen directory

## Prerequisites

- Python 3.x
- PyQt5
- Requests library
- Discord Developer Account

## Setup

### 1. Discord Application Configuration

1. Visit [Discord Developer Portal](https://discord.com/developers/applications/)
2. Create a new application
3. Navigate to the OAuth2 section
4. Add `http://localhost:8000/callback` to your Redirect URIs
5. Copy your Client ID and Client Secret

### 2. Configuration File

Create a `config.py` file in the project root with the following content:

```python
CLIENT_ID = 'your_client_id_here'
CLIENT_SECRET = 'your_client_secret_here'
REDIRECT_URI = 'http://localhost:8000/callback'
SCOPE = 'identify email'
```

### 3. Dependencies Installation

```bash
pip install PyQt5 requests
```

## Usage

1. **Run the Application:**
   ```bash
   python gui.py
   ```

2. **Authentication:**
   - Click "Connect to Discord" button
   - Authorize the application in your web browser
   - Application will save basic user information

3. **Select Directories:**
   - Choose the directory containing your Discord message data
   - Select a save directory for the message ID list
   - Optionally exclude specific channel IDs

4. **Generate Message ID List:**
   - Click "Generate Message ID List"
   - View progress in the Console tab
   - Find the generated `messages.txt` in your chosen save directory

5. **Submit to Discord:**
   - Use the generated message ID list when contacting Discord Support

## Troubleshooting

- Ensure you have the latest version of Python
- Verify your Discord application settings
- Check that all dependencies are installed
- Make sure you have the necessary permissions in your Discord account

## Future Improvements

- Automatic email generation for deletion requests
- Enhanced error handling
- Support for more complex message filtering

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.