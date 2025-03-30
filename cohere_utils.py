import cohere
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()
co = cohere.Client(os.getenv("COHERE_API_KEY"))

def extract_json_from_response(text):
    """
    Extracts JSON object from code block if it's wrapped in triple backticks.
    """
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    else:
        # fallback if response is just raw JSON
        return json.loads(text.strip())

def get_trivia_question_from_prompt(prompt, temperature=0.7):
    response = co.chat(
        model="command-r-plus",  # or "command-r"
        message=prompt,
        temperature=temperature,
        max_tokens=400,
    )

    text = response.text.strip()

    try:
        return extract_json_from_response(text)
    except json.JSONDecodeError as e:
        raise ValueError("Could not parse Cohere's response as JSON:\n" + text)