import requests
import base64
from secrets import USER_CLIENT_ID, USER_CLIENT_SECRET, USER_REDIRECT_URI, spotify_user_id
from urllib.parse import urlencode
import json
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

# using OAuth we create a link to redirect user to their spotify account
def create_oauth_link():
    params = {
        "client_id": USER_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": USER_REDIRECT_URI,
        "scope": "user-read-private user-read-email"
    }
    endpoint = "https://accounts.spotify.com/authorize"
    response = requests.get(endpoint, params=params)
    url = response.url
    return url

# authorization process to exchange code for token
# you can either pass client credentials either in the body or header base64 encoding
def exchange_code_token(code=None):
    code_params = {
        "grant_type": "client_credentials",
        "code": str(code),
        "redirect_uri": USER_REDIRECT_URI,
        "client_id": USER_CLIENT_ID,
        "client_secret": USER_CLIENT_SECRET,
    }
    #client_cred = f"{USER_CLIENT_ID}:{USER_CLIENT_SECRET}"
    #client_cred_b64 = base64.b64encode(client_cred.encode()).decode()
    #headers = {"Authorization": f"Basic {client_cred_b64}"}
    
    s_endpoint = "https://accounts.spotify.com/api/token"
    s_response = requests.post(s_endpoint, data=code_params).json()
    return s_response["access_token"]
    
# get user data
user_id = spotify_user_id
def print_user_info(user_id, access_token=None):
    headers = {"Authorization": f"Bearer {access_token}"}
    endpoint = f"https://api.spotify.com/v1/users/{user_id}"
    response = requests.get(endpoint, headers=headers).json()
    name = response['display_name']
    return f"name: {name}"
    
# get user playlists
playlist_dct = {}
def get_user_playlists(user_id, access_token=None):
    headers = {"Authorization": f"Bearer {access_token}"}
    endpoint = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    response = requests.get(endpoint, headers=headers).json()

    for item in response["items"]:
        playlist_name = item["name"]
        playlist_id = item["id"]
        playlist_dct[playlist_name] = playlist_id
        print(
            f"Playlist name: {playlist_name} | Playlist ID: {playlist_id}"
        )

# choose playlist
playlist_items_dct = {}
playlist_items_list = [] 
def get_playlist_items(playlist_id, access_token=None):
    headers = {"Authorization": f"Bearer {access_token}"}
    endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    params = {
        "market": "KE",
        "fields": "fields=items(track(artists,name))"
    }
    response = requests.get(endpoint, params=params, headers=headers).json()

    for item in response["items"]:
        track_name = item["track"].get("name")
        artist_name = item["track"]["artists"][0].get("name")
        playlist_items_dct[track_name] = artist_name
        playlist_items_list.append(f"{track_name}+{artist_name}")

        print(f"Track Name: {track_name} | Artist's Name: {artist_name}")

# Define scopes
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def youtube_oauth():
    # Disable OAuthlib's HTTPS verification when running locally
    # DO NOT leave this enabled during production
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    clients_secret_file = "client_secret_desktop.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(clients_secret_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)
    return youtube

def create_youtube_playlist(youtube_credentials, plist_name, youtube_playlist_description):
    request = youtube_credentials.playlists().insert(
        part="snippet,status",
        body={
            "snippet":{
                "title": f"{plist_name}",
                "description": f"{youtube_playlist_description}"
            },
            "status": {
                "privacyStatus": "private"
            }
        }
    )

    response = request.execute()
    youtube_playlist_id = response["id"]    
    return youtube_playlist_id

video_ids_list = []
def search_youtube_titles(playlist_items_list, youtube_credentials):
    for search_query in playlist_items_list:
        request = youtube_credentials.search().list(
            part="snippet",
            maxResults=1,
            q=search_query
        )
        
        response = request.execute()

        for item in response["items"]:
            video_id = item["id"].get("videoId")
            #video_title = item["snippet"].get("title")
            video_ids_list.append(video_id)

def insert_videos_to_playlist(youtube_playlist_id, video_ids_list, youtube_credentials):
    for id in video_ids_list:
        request = youtube_credentials.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": youtube_playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": id
                    }
                }
            }
        )

        response = request.execute()




def main():
    link = create_oauth_link()
    print(f"Follow the link to start the authentication with Spotify: {link}")
    code = input("Spotify Code: ")
    #exchange_code_token(code)
    access_token = exchange_code_token(code)
    print(print_user_info(user_id, access_token=access_token))
    get_user_playlists(user_id, access_token=access_token)
    print("*" * 20)
    plist_name = input("Enter Playlist Name from the results above: ")
    playlist_id = playlist_dct.get(plist_name)
    get_playlist_items(playlist_id, access_token=access_token)
    youtube_credentials = youtube_oauth()
    youtube_playlist_description = input("Please enter Youtube playlist description: ")
    print("*" * 20)
    print(f"Creating {plist_name} on Youtube...")
    youtube_playlist_id = create_youtube_playlist(youtube_credentials, plist_name, youtube_playlist_description)
    print("*" * 20)
    print("Searching for titles...")
    search_youtube_titles(playlist_items_list, youtube_credentials)
    print("*" * 20)
    print(f"Inserting videos to {plist_name} playlist...")
    insert_videos_to_playlist(youtube_playlist_id, video_ids_list, youtube_credentials)
    print("*" * 20)
    print(f"Successfully created {plist_name}!!!")


if __name__ == "__main__":
    main()

