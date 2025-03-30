def generate_trivia_prompt(track):
    """
    Generates a prompt that asks the LLM to create a trivia question based on one song.
    The LLM is responsible for selecting the question type, distractors, and ensuring realism.
    """

    prompt = f"""
You are a smart music trivia generator.

Your task is to create a single multiple-choice question (with 4 answer options) based on the song information below.

**Guidelines**:
- The question must be factually correct and based on real knowledge of the song, artist, or album.
- Choose one of these types (but choose intelligently): 
    - When was this song or album released?
    - What is the album name of the song?
    - Who is the artist of the song?
    - Which of these songs is by this artist?
    - Which song is from this album?
    - Which one is NOT from this album?
- Make distractors challenging — avoid random or obviously wrong answers. Use your own knowledge to make them close but incorrect (e.g., artists from the same genre/era, songs with similar names, albums from similar years).
- Always generate exactly 4 options and specify the correct answer.
- Do NOT include any explanation or commentary.

**Song Information**:
- Title: "{track['title']}"
- Artist: "{track['artist']}"
- Album: "{track['album']}"
- Release Date: "{track['release_date']}"

Respond ONLY with a valid JSON object, and wrap your response in triple backticks with the `json` language tag, like this:

```json
{{
  "question": "...",
  "options": ["...", "...", "...", "..."],
  "answer": "..."
}}
```
"""
    return prompt.strip()