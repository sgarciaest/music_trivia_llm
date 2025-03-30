import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

SCOPE = "user-library-read playlist-read-private"

def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope=SCOPE,
        cache_path=".spotify_cache"  # local token storage
    )

def get_token_from_code(code):
    sp_oauth = get_spotify_oauth()
    return sp_oauth.get_access_token(code, as_dict=False)

def get_auth_url():
    sp_oauth = get_spotify_oauth()
    return sp_oauth.get_authorize_url()

def get_spotify_client_from_token(token):
    return spotipy.Spotify(auth=token)

def is_token_cached():
    sp_oauth = get_spotify_oauth()
    return sp_oauth.get_cached_token() is not None

def get_cached_spotify_client():
    sp_oauth = get_spotify_oauth()
    token_info = sp_oauth.get_cached_token()
    if token_info:
        return spotipy.Spotify(auth=token_info['access_token'])
    return None

def get_user_saved_tracks(sp, limit=50, show_progress=False):
    tracks = []
    total = sp.current_user_saved_tracks(limit=1)["total"]

    if show_progress:
        import streamlit as st
        progress_bar = st.progress(0)
        loaded = 0

    results = sp.current_user_saved_tracks(limit=limit, offset=0)
    while results:
        for item in results["items"]:
            track = item["track"]
            tracks.append({
                "title": track["name"],
                "artist": track["artists"][0]["name"],
                "album": track["album"]["name"],
                "release_date": track["album"]["release_date"]
            })

        if show_progress:
            loaded += len(results["items"])
            progress_bar.progress(min(loaded / total, 1.0))

        if results["next"]:
            results = sp.next(results)
        else:
            break

    if show_progress:
        progress_bar.empty()

    return tracks

