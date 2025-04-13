import streamlit as st
import os
import random
from collections import Counter
from datetime import datetime

from spotify_utils import (
    get_auth_url,
    get_token_from_code,
    get_spotify_client_from_token,
    get_cached_spotify_client,
    is_token_cached,
    get_user_saved_tracks
)
from cohere_utils import get_trivia_question_from_prompt
from trivia_generator import generate_trivia_prompt, get_album_and_artist_strengths

# st.set_page_config(page_title="Music Trivia", layout="wide", page_icon="📀")
st.set_page_config(page_title="Music Trivia", layout="wide", page_icon=":material/lyrics:")

st.title("🎧 Music Trivia")

# --- Sidebar: User Info and Auth ---
with st.sidebar:
    st.header("👤 Spotify User")

    sp = None
    if is_token_cached():
        sp = get_cached_spotify_client()
        profile = sp.current_user()

        st.success("Logged in!")

        if profile.get("images"):
            name = profile['display_name']
            image_url = profile["images"][0]["url"]

            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 10px;">
                <img src="{image_url}" width="35" style="border-radius: 50%; margin-top: 2px;" />
                <strong>{name}</strong>
            </div>
            <div style="margin-bottom: 20px;"></div>
            """, unsafe_allow_html=True)

        if st.button("Logout"):
            os.remove(".spotify_cache")
            st.session_state.clear()
            st.rerun()
    else:
        st.warning("Not logged in")
        if st.button("Login with Spotify"):
            auth_url = get_auth_url()
            st.markdown(f"[Click here to log in with Spotify]({auth_url})", unsafe_allow_html=True)

# --- Main Area ---
if is_token_cached() and sp:
    # Load saved tracks
    if "user_tracks" not in st.session_state:
        st.subheader("🎵 Loading your saved tracks...")
        with st.spinner("Fetching from Spotify..."):
            tracks = get_user_saved_tracks(sp, limit=50, show_progress=True)
            st.session_state.user_tracks = tracks
            st.success(f"✅ Loaded {len(tracks)} tracks.")
    else:
        tracks = st.session_state.user_tracks

    # --- Sidebar: Show music library stats ---
    with st.sidebar:
        st.divider()
        st.subheader("🎶 Your Library Stats")
        st.write(f"- **Total tracks**: {len(tracks)}")
        st.write(f"- **Unique artists**: {len(set(t['artist'] for t in tracks))}")
        st.write(f"- **Unique albums**: {len(set(t['album'] for t in tracks))}")

        # First and last songs
        added_dates = sorted([t['release_date'] for t in tracks if t['release_date']])
        if added_dates:
            st.write(f"- **Oldest released song**: {added_dates[0]}")
            st.write(f"- **Newest released song**: {added_dates[-1]}")

        # # Decade analysis
        # years = [int(t['release_date'][:4]) for t in tracks if t['release_date'][:4].isdigit()]
        # decades = [f"{(y // 10) * 10}s" for y in years]
        # most_common_decades = Counter(decades).most_common(3)
        # st.write("**Top decades:**")
        # for d, count in most_common_decades:
        #     st.write(f"- {d} ({count} songs)")

        # Trivia Stats
        st.divider()
        st.subheader("📊 Trivia Stats")

        total = st.session_state.get("total_attempts", 0)
        correct = st.session_state.get("correct_answers", 0)

        if total == 0:
            st.write("No trivia played yet.")
        else:
            pct = (correct / total) * 100
            st.write(f"**Score:** {correct}/{total} ({pct:.1f}%)")

            history = st.session_state.get("trivia_history", [])
            if history:
                st.write("**Last 5 answers:**")
                st.write(" ".join(history))

    # --- Trivia Logic ---
    st.subheader("Test your music knowledge!")
    strong_albums, strong_artists = get_album_and_artist_strengths(tracks)

    if "current_trivia" not in st.session_state and "trivia_result" not in st.session_state:
        if st.button("🎲 Generate a Trivia Question"):
            with st.spinner("Generating... 🤔"):
                main_track = random.choice(tracks)
                prompt = generate_trivia_prompt(main_track, strong_albums, strong_artists)
                try:
                    trivia = get_trivia_question_from_prompt(prompt)
                    st.session_state.current_trivia = trivia
                except Exception as e:
                    st.error("Failed to generate trivia.")
                    st.exception(e)

    # --- Display Question and Options ---
    if "current_trivia" in st.session_state:
        trivia = st.session_state.current_trivia
        st.markdown(f"**📝 Q: {trivia['question']}**")

        for option in trivia["options"]:
            if st.button(option):
                st.session_state.trivia_result = {
                "question": trivia["question"],
                "selected": option,
                "correct": trivia["answer"],
                "options": trivia["options"],
                "is_correct": option == trivia["answer"]
                }

                # Update stats
                st.session_state.total_attempts = st.session_state.get("total_attempts", 0) + 1
                st.session_state.correct_answers = st.session_state.get("correct_answers", 0) + int(option == trivia["answer"])
                history = st.session_state.get("trivia_history", [])
                history.append("✅" if option == trivia["answer"] else "❌")
                st.session_state.trivia_history = history[-5:]
                del st.session_state.current_trivia
                st.rerun()

    # --- Show Feedback ---
    if "trivia_result" in st.session_state:
        result = st.session_state.trivia_result
        st.markdown(f"**📝 Q: {result['question']}**")
        for option in [result["selected"]] + [o for o in result["options"] if o != result["selected"]]:
            st.button(option, disabled=True)

        if result["is_correct"]:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Incorrect. The correct answer was: **{result['correct']}**")

        if st.button("➡️ Next Question"):
            del st.session_state.trivia_result
            st.rerun()

# --- Handle redirect after login ---
else:
    query_params = st.query_params
    code = query_params.get("code")
    if code:
        token = get_token_from_code(code)
        if token:
            st.success("✅ Spotify login successful! Reloading...")
            st.query_params.clear()
            st.rerun()
