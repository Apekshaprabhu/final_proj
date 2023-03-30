import spotipy
from spotipy.oauth2 import SpotifyOAuth
username = "apeksh@gmail.com"
client_id = '84605e926cc941d191f8263ead2accad'
client_secret = '703230a9f2c846b6bf28a6d2d91da2fc'
redirect_uri = "https://open.spotify.com/callback/"

scope = "user-read-playback-state,user-modify-playback-state"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri))

devices = sp.devices()
for device in devices['devices']:
    print(device['name'], device['id'])
