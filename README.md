## Discord Rich Presence for Plex, made in Python

### Requirements:
- Python (Latest) (https://python.org)
- Discord Client (Latest) (https://discord.com)

---

### Setup:
1. Open CMD/Terminal and path to directory
2. Run "pip install -r requirements.txt"
3. Edit settings.py (See: [Settings](#settings))
4. Launch the script (See: [Launching via CMD/Terminal](#launching-via-cmdterminal))

---

### Settings:
- Debug mode: True/False, prints some information if enabled
- Discord application ID: Your Discord rich presence application ID
    - https://discord.com/developers/applications
    - Sign in, create a new application, and paste its application ID (or use the default one)
- Refresh time: The amount of time it takes for the rich presence status to update
    - Minimum is 5 seconds for rate-limit reasons
- Plex username: The username of the Plex account used to collect information from
    - This helps to identify you when there are multiple managed users on one account
- Plex API Token: This is the token that your Plex account uses for authentication
    - https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/
    - Don't worry! No information is sent anywhere besides to your Plex Media Server.
- Plex Media Server IP: This is the IP that your Plex Media Server is hosted on. You'll need it in order for the application to get the API information.

---

### Launching via CMD/Terminal:
1. Windows:
   - >py main.py
   - >python main.py
2. Linux: 
   - >./main.py  
   - >python3 main.py

Or create your own launch script!