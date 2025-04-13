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
- In general the question should be focused on the song info provided (title, artist, album, release date). If specified below, you can (or not, up to you) generate specific questions about an album or an artist forgetting the song, and using your music knowledge to do it.

"""

    if album_ok:
        prompt += "- You ARE allowed to ask about the album. The user probably has sufficient knowledge on the album based on the number of saved songs of the album in his library. \n"
    else:
        prompt += "- Do NOT ask about the album — the user may not know it well enough.\n"

    if artist_ok:
        prompt += "- You ARE allowed to ask about the artist.  The user probably has sufficient knowledge on the artist based on the number of saved songs of the artist in his library. \n"
    else:
        prompt += "- Do NOT ask questions that require deep artist knowledge.\n"

    prompt += """
- Make distractors challenging — avoid random or obviously wrong answers. Use your own music knowledge to make them close but incorrect (e.g., artists from the same genre/era, songs with similar names, albums from similar years).
- Always generate exactly 4 options and specify the correct answer.
- Do NOT include any explanation or commentary.
- When showing release dates options, don't show options with a full date (e.g. 2022-03-14). Show only years.
- Do NOT use negation (e.g. "was NOT released") to form questions. Avoid reverse logic or trick-question phrasing.
- Do not create questions that refer to songs absent from the provided set of albums. For instance, avoid questions such as: “Which of the following albums by (artist) does not include the song (title)?”
- If a question focuses on a specific song, include all relevant details from the available metadata except the one being asked about. For example:
    - If the question is about the release year, also mention the song's artist and album name.
    - If asking which album a song appears on, also provide the artist name and release year.
- The main sentence of each question must explicitly reference at least one data point from the provided song metadata—either the song title, album name, or artist name. You may use external music knowledge to construct context or plausible answer choices, but the core focus of the question must remain tied to actual items present in the provided information.

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
