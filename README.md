# discord messages delete helper
decided on the idea from: https://github.com/ishnz/bulk_deletion_helper

This version of the code works slightly better in my opinion. there were a few problems in the original code when trying to find the discord package file and where to create the messages.txt file

Am planning on creating a application with this where you can select where the files are located, it then creates the msg file, then it goes onto discord support and requests for the deletion of these message or simply create the msg file for you to request deletion yourself.

# Bot configuration
https://discord.com/developers/applications/
In config.py add your application client ID and client secret. also include 'http://localhost:8000/callback'
in the redirects URL that is located in the Oath2 section of your discord application

# config setup
create a file called 'config.py' and this is what you need to add to your config.py file:

CLIENT_ID = '...'
CLIENT_SECRET = '...'
REDIRECT_URI = 'http://localhost:8000/callback'
SCOPE = 'identify email'