from flask import Flask, render_template, request
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)

# Replace with your client ID and client secret obtained from the Spotify Developer Dashboard
client_id = '966596594f2b4bcd9139cbb7bbf701f4'
client_secret = 'd7acd4bdc3104e178aeb67246e2e8620'

# Authenticate your application by requesting an access token
auth_manager = SpotifyClientCredentials(
    client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

track_uri = ''


@app.route('/')
def index():
    return render_template('index1.html')


@app.route('/search', methods=['POST'])
def search():
    global track_uri
    query = request.form['query']
    track_results = sp.search(q='track:' + query, type='track', limit=1)

    if len(track_results['tracks']['items']) > 0:
        track_uri = track_results['tracks']['items'][0]['uri']
        return 'success'
    else:
        return 'error'


@app.route('/play')
def play():
    if track_uri != '':
        sp.start_playback(uris=[track_uri])
        return 'success'
    else:
        return 'error'


@app.route('/pause')
def pause():
    sp.pause_playback()
    return 'success'


if __name__ == '__main__':
    app.run(debug=True)
