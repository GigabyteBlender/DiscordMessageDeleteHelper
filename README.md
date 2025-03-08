# Discord Message Delete Helper

Discord Message Delete Helper is a Python application designed to assist users in generating a list of Discord message IDs. This list can then be used to request the deletion of those messages from Discord support.

## Why was this made?

Discord's approach to message deletion has been a source of frustration for many users. The platform currently does not provide an official method for bulk deleting messages, which has led to the development of workarounds and third-party solutions13.

The reasons behind this decision are multifaceted:

Preserving Context: Discord claims that retaining messages is necessary to maintain context in conversations, especially for collaborative projects or communities that rely on historical information.

Technical Limitations: Mass deletion of messages can put a significant strain on Discord's database, which led to the removal of bulk deletion features in the past4.

Privacy and Security Concerns: Discord's privacy policy prevents them from reviewing message content without cause, which complicates the process of verifying requests for mass deletion1.

Compliance with Regulations: Discord must balance user requests with legal requirements like GDPR's Right to Erasure, which has led to changes in how they handle deletion requests1.

To address these issues while still providing some level of control to users, Discord has implemented the following measures:

Allowing users to request their data package and submit message IDs for deletion3.

Deleting messages on both sides in private DMs but retaining placeholders in server or group chats.

Gradually adapting their approach to GDPR compliance has affected how deletion requests are processed1.

These measures, however, are often seen as inadequate by users who desire more control over their message history. The lack of an official bulk deletion feature has led to the creation of unofficial methods and tools, which can potentially violate Discord's terms of service and risk account suspension6.

In response to this demand, some users have developed methods to generate lists of message IDs from the data provided by Discord, which can then be submitted for deletion. This approach aims to provide a compromise between 

## Features

- **Generate Message ID List:** Easily compile a list of message IDs that you wish to delete.
- **User-Friendly:** Simple and intuitive interface for seamless user experience.
- **Python-Based:** Leverages the power of Python for efficient processing.

## Usage

1. **Run the Application:** Execute the Python script to start the application.
2. **Select Messages:** Choose the messages you wish to delete.
3. **Generate ID List:** The application will generate a list of message IDs.
4. **Submit to Discord Support:** Use the generated list to request deletion from Discord support.

## Bot Configuration

1. Visit [Discord Developer Portal](https://discord.com/developers/applications/).
2. In `config.py`, add your application client ID and client secret.
3. Include `http://localhost:8000/callback` in the redirect URLs located in the OAuth2 section of your Discord application.

## Config Setup

Create a file called `config.py` and add the following:

```python
CLIENT_ID = '...'
CLIENT_SECRET = '...'
REDIRECT_URI = 'http://localhost:8000/callback'
SCOPE = 'identify email'
