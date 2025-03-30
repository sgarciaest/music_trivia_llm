from collections import Counter

def get_album_and_artist_strengths(tracks):
    album_counts = Counter([t['album'] for t in tracks])
    artist_counts = Counter([t['artist'] for t in tracks])

    strong_albums = {album for album, count in album_counts.items() if count >= 3}
    strong_artists = {artist for artist, count in artist_counts.items() if count >= 5}

    return strong_albums, strong_artists

def generate_trivia_prompt(track, strong_albums, strong_artists):
    album = track["album"]
    artist = track["artist"]

    album_ok = album in strong_albums
    artist_ok = artist in strong_artists

    prompt = f"""
You are a smart music trivia generator.

Your task is to create a single multiple-choice question (with 4 answer options) based on the song information below.

**Guidelines**:
- The question must be factually correct and based on real knowledge of the song, artist, or album.
- Choose one of these types **intelligently**:
    - When was this song by this artist released?
    - What is the album name of the song by this artist?
    - Who is the artist of the song?
    - Which of these songs is by this artist?
    - Which song is from this album?

"""

    if album_ok:
        prompt += "- You ARE allowed to ask about the album (e.g., album release year, songs on the album, which song doesn't belong).\n"
    else:
        prompt += "- Do NOT ask about the album — the user may not know it well enough.\n"

    if artist_ok:
        prompt += "- You ARE allowed to ask about the artist (e.g., which songs are by them).\n"
    else:
        prompt += "- Do NOT ask questions that require deep artist knowledge.\n"

    prompt += """
- Make distractors challenging — avoid random or obviously wrong answers. Use your own music knowledge to make them close but incorrect (e.g., artists from the same genre/era, songs with similar names, albums from similar years).
- Always generate exactly 4 options and specify the correct answer.
- Do NOT include any explanation or commentary.

**Song Information**:
- Title: "{title}"
- Artist: "{artist}"
- Album: "{album}"
- Release Date: "{release_date}"

Respond ONLY with a valid JSON object, and wrap your response in triple backticks with the `json` language tag, like this:

```json
{{
  "question": "...",
  "options": ["...", "...", "...", "..."],
  "answer": "..."
}}
"""
    return prompt.strip().format(**track)
