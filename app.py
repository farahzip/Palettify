from flask import Flask, render_template, request
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
from io import BytesIO
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Set up Spotify API credentials
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SCOPE = "user-library-read user-top-read playlist-modify-public"

# Initialize Spotify API client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=SCOPE))

# Extract dominant color from an image
def extract_colors_from_image(image_url):
    try:
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        img = img.resize((img.width // 10, img.height // 10))  # Resize for faster processing
        img = img.convert('RGB')

        np_img = np.array(img).reshape((-1, 3))  # Reshape to list of RGB values
        kmeans = KMeans(n_clusters=1, random_state=42)
        kmeans.fit(np_img)
        dominant_color = kmeans.cluster_centers_[0]

        return {"dominant": tuple(dominant_color.round().astype(int))}
    except Exception as e:
        print(f"Error extracting color: {e}")
        return {"dominant": (0, 0, 0)}

# Fetch top tracks
def get_top_tracks(time_range="medium_term", limit=10):
    results = sp.current_user_top_tracks(time_range=time_range, limit=limit)
    tracks = []
    seen_colors = set()

    for item in results.get('items', []):
        image_url = item['album']['images'][0]['url']
        colors = extract_colors_from_image(image_url)
        dominant_color = tuple(colors["dominant"])

        if dominant_color in seen_colors:
            continue

        tracks.append({
            "name": item['name'],
            "artist": item['artists'][0]['name'],
            "album": item['album']['name'],
            "url": item['external_urls']['spotify'],
            "uri": item['uri'],
            "colors": colors,
            "album_image": image_url
        })
        seen_colors.add(dominant_color)

    return tracks

# Fetch top artists
def get_top_artists(time_range="medium_term", limit=10):
    results = sp.current_user_top_artists(time_range=time_range, limit=limit)
    artists = []
    seen_colors = set()

    for item in results.get('items', []):
        image_url = item['images'][0]['url']
        colors = extract_colors_from_image(image_url)
        dominant_color = tuple(colors["dominant"])

        if dominant_color in seen_colors:
            continue

        artists.append({
            "name": item['name'],
            "url": item['external_urls']['spotify'],
            "uri": item['uri'],
            "colors": colors,
            "image": image_url
        })
        seen_colors.add(dominant_color)

    return artists

# Create playlist and add tracks
def create_playlist(name, tracks):
    user_id = sp.current_user()["id"]
    playlist = sp.user_playlist_create(user=user_id, name=name, public=True)
    track_uris = [track['uri'] for track in tracks]
    if track_uris:
        sp.playlist_add_items(playlist_id=playlist['id'], items=track_uris)
    return playlist['external_urls']['spotify']

@app.route("/", methods=["GET", "POST"])
def index():
    time_range = request.form.get("time_range", "medium_term")
    limit = int(request.form.get("limit", 5))
    content_type = request.form.get("content_type", "tracks")
    create_playlist_flag = request.form.get("create_playlist") == "true"

    if content_type == "tracks":
        data = get_top_tracks(time_range, limit)
        playlist_url = None
        if create_playlist_flag and data:
            playlist_url = create_playlist("Palettify Top Tracks", data)
    else:
        data = get_top_artists(time_range, limit)
        playlist_url = None

    return render_template("index.html", data=data, playlist_url=playlist_url, content_type=content_type)

if __name__ == "__main__":
    app.run(debug=True)
