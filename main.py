import streamlit as st
import os
from spotify_utils import (
    get_auth_url,
    get_token_from_code,
    get_spotify_client_from_token,
    get_cached_spotify_client,
    is_token_cached,
    get_user_saved_tracks
)
import random
from cohere_utils import get_trivia_question_from_prompt
from trivia_generator import generate_trivia_prompt, get_album_and_artist_strengths

st.set_page_config(page_title="Spotify Seamless Auth", layout="centered")
st.title("🎧 Spotify Login")

sp = None

# --- Check if user is already authenticated ---
if is_token_cached():
    sp = get_cached_spotify_client()
    st.success("✅ You're logged in with Spotify!")

    profile = sp.current_user()
    st.write(f"Welcome, **{profile['display_name']}**!")
    if profile.get("images"):
        st.image(profile["images"][0]["url"], width=100)

    # --- Load tracks only once and cache them ---
    if "user_tracks" not in st.session_state:
        st.subheader("🎵 Loading your saved tracks...")
        with st.spinner("Fetching your saved songs from Spotify..."):
            tracks = get_user_saved_tracks(sp, limit=50, show_progress=True)
            st.session_state.user_tracks = tracks
            st.success(f"✅ Loaded {len(tracks)} tracks!")
    else:
        tracks = st.session_state.user_tracks
        st.success(f"🎶 {len(tracks)} saved tracks loaded from session.")

    # --- Show tracks ---
    st.subheader("🎶 Your Latest Saved Tracks")
    for t in tracks[:5]:  # display only first 20 for UI performance
        st.markdown(f"- **{t['title']}** by {t['artist']} (released on {t['release_date']})")
    
    # --- Trivia Generator ---
    st.divider()
    st.subheader("🧠 Music Trivia Preview")

    if len(tracks) < 10:
        st.warning("Not enough saved songs to generate trivia. Please save more songs in your Spotify.")
    else:
        # Compute strong albums/artists once
        strong_albums, strong_artists = get_album_and_artist_strengths(tracks)

        if st.button("🎲 Generate a Trivia Question"):
            with st.spinner("Thinking... 🤔"):
                main_track = random.choice(tracks)

                # Generate prompt with personalization logic
                prompt = generate_trivia_prompt(main_track, strong_albums, strong_artists)

                try:
                    trivia = get_trivia_question_from_prompt(prompt)
                    st.session_state.current_trivia = trivia
                except Exception as e:
                    st.error("Failed to generate trivia.")
                    st.exception(e)


    # Show trivia question if available
    if "current_trivia" in st.session_state:
        trivia = st.session_state.current_trivia
        st.write(f"**Q: {trivia['question']}**")

        for option in trivia["options"]:
            if st.button(option):
                if option == trivia["answer"]:
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Incorrect. The correct answer was: **{trivia['answer']}**")
                del st.session_state.current_trivia
                st.rerun()


# --- Handle login redirect with code ---
else:
    query_params = st.query_params
    code = query_params.get("code")

    if code:
        token = get_token_from_code(code)
        if token:
            st.success("✅ Spotify login successful! Reloading...")
            st.query_params.clear()
            st.rerun()
        else:
            st.error("⚠️ Could not authenticate. Try again.")
    else:
        st.warning("You are not authenticated.")
        if st.button("Login with Spotify"):
            auth_url = get_auth_url()
            st.markdown(f"[Click here to log in with Spotify]({auth_url})", unsafe_allow_html=True)

# --- Logout option ---
if os.path.exists(".spotify_cache"):
    if st.button("Logout"):
        os.remove(".spotify_cache")
        st.session_state.clear()
        st.rerun()
