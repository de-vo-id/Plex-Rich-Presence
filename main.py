import pypresence
import requests
import xmltodict
import time

import settings

## ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ##

debug_mode = settings.settings["Debug_Mode"]
app_id = settings.settings["Discord_Application_ID"]
refresh_time = settings.settings["Refresh_Time"]
plex_user = settings.settings["Plex_Username"]
api_key = settings.settings["Plex_API_Token"]
server_ip = settings.settings["Plex_Server_IP"]

if not app_id or not plex_user or not api_key or not server_ip:
    if not app_id:
        print("Discord Application ID not given in settings.")
    if not refresh_time:
        print("Refresh time not given in settings.")
    if not plex_user:
        print("Plex username not given in settings.")
    if not api_key:
        print("Plex API Key not given in settings.")
    if not server_ip:
        print("Plex Server IP not given in settings.")
    quit()

if refresh_time < 5:
    refresh_time = 5

## ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ##

rpc = pypresence.Presence(app_id)
rpc.connect()

print("""
 -*#%%%%%%%%%%%%%%%%%%%%%%#*- 
+%%=.                    .=#%+
%%:      -=====:           .%%
%%.       :+++++-           %%
%%.        :+++++-          %%
%%.         .=++++=         %%
%%.          .=++++=.       %%
%%.           .+++++=       %%
%%.           =++++=.       %%
%%.         .=++++=         %%
%%.        :+++++-          %%
%%.       :+++++-           %%
%%:      -=====:           .%%
+%#=.                    .-#%*
 -*#%%%%%%%%%%%%%%%%%%%%%%#*- 

Plex Rich Presence
https://github.com/de-vo-id
""")

## ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ##

needs_update = True
previous_offset = 0

while True: # Main loop
    response = requests.get(f'http://{server_ip}:32400/status/sessions?X-Plex-Token={api_key}') # Get data from Plex API
    if response.status_code == 200: # If successful query
        try:
            user_found = False
            data_dict = xmltodict.parse(response.text)
            sessions = data_dict.get('MediaContainer', {}).get('Video', []) # Split video sessions
                
            if not isinstance(sessions, list): # Ensure that sessions are always in a list for ease of access; if only 1 session then it just comes out as dict and that causes issues
                sessions = [sessions] 

            for session in sessions: # Going through each session
                if session.get('User', {}).get('@title') == plex_user:
                    user_found = True
                    media_type = ""
                    season = str(int(session.get('@parentIndex', 0)))
                    episode_number = str(int(session.get('@index', 0)))
                    episode_info = f"S{season.zfill(2)}E{episode_number.zfill(2)}"

                    if str(episode_number) == "0" and str(season) == "0":
                        media_type = "Movie"
                    else:
                        media_type = "Show"

                    state = session['Player']['@state']

                    raw_offset = int(session['@viewOffset'])
                    view_offset = (raw_offset // 1000) if (raw_offset > 1000) else (raw_offset+1000 // 1000) # Needs this if else otherwise it errors because start needs to be >= 1 second
                    duration = int(session['@duration']) // 1000
                    remaining_time = duration - view_offset

                    if abs(view_offset - previous_offset) > refresh_time + (refresh_time // 2): # Checks for difference in time offsets and triggers needs_update (mainly for checking for time skips)
                        previous_offset = view_offset
                        needs_update = True

                    if state == 'playing' and needs_update == True: # If media is playing and requires a RPC update
                        end_time = int(time.time()) + remaining_time # Convert to epoch time for Discord BS
                        if media_type == "Show": # If media has season numbers
                            line1 = f"{session.get('@grandparentTitle', 'Show Title')} [{episode_info}]"
                            line2 = session.get('@title', 'Show Episode')
                            rpc.update(
                                details=line1,
                                state=line2,
                                large_image='plex',
                                large_text="Plex Media Player",
                                small_image='playing' if state == 'playing' else 'paused',
                                small_text="Playing" if state == 'playing' else 'Paused',
                                start=view_offset,
                                end=end_time
                            )
                        elif media_type == "Movie": # If media does not have season numbers
                            line1 = f"{session.get('@title', 'Movie title')} ({session.get('@year', '0000')})"
                            rpc.update(
                                details=line1,
                                large_image='plex',
                                large_text="Plex Media Player",
                                small_image='playing' if state == 'playing' else 'paused',
                                small_text="Playing" if state == 'playing' else 'Paused',
                                start=view_offset,
                                end=end_time
                            )
                        needs_update = False
                        if debug_mode ==  True:
                            print('[RPC Update]: Media playing')
                    elif state == 'playing' and needs_update == False: # If media is playing and does not require a RPC update
                        needs_update = False
                    else: # If media is paused
                        if media_type == "Show": # If media has season numbers
                            line1 = f"{session.get('@grandparentTitle', 'Show Title')} [{episode_info}]"
                            line2 = session.get('@title', 'Show Episode')
                            rpc.update(
                                details=line1,
                                state=line2,
                                large_image='plex',
                                large_text="Plex Media Player",
                                small_image='playing' if state == 'playing' else 'paused',
                                small_text="Playing" if state == 'playing' else 'Paused',
                            )
                        elif media_type == "Movie": # If media does not have season numbers
                            line1 = f"{session.get('@title', 'Movie title')} ({session.get('@year', '0000')})"
                            rpc.update(
                                details=line1,
                                large_image='plex',
                                large_text="Plex Media Player",
                                small_image='playing' if state == 'playing' else 'paused',
                                small_text="Playing" if state == 'playing' else 'Paused',
                            )
                        needs_update = True
                        if debug_mode ==  True:
                            print('[RPC Update]: Media paused')
                    break

            if user_found == False: # If user is not found in active sessions retrieved from API
                rpc.update(
                    details="Browsing",
                    large_image='plex',
                    large_text="Plex Media Player",
                    small_image='none'
                )
                needs_update = True
                if debug_mode ==  True:
                    print('[RPC Update]: Browsing')

        except Exception as exception:
            print(f'[RPC Refresh Error]: {exception}')
    else:
        print(f'[API Error]: {response.status_code}')

    time.sleep(refresh_time) # Wait for specified amount of time
