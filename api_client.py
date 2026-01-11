import requests
import os
import json
import google.generativeai as genai
from datetime import datetime

WORKER_URL = "https://linkedin-pinpoint-worker.gdgdughdshf.workers.dev/today/BloggingIo@7"

def fetch_daily_data():
    """Fetches the daily Pinpoint answer and clues."""
    try:
        response = requests.get(WORKER_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            return data["data"]
        else:
            print("API returned success=False")
            return None
    except Exception as e:
        print(f"Error fetching daily data: {e}")
        return None

def generate_plausible_guesses(clues, correct_answer):
    """
    Uses Gemini to generate plausible but incorrect guesses based on the clues.
    This makes the gameplay look human (trial and error).
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found. Skipping plausible guesses.")
        return []

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    prompt = f"""
    I am playing a game called Pinpoint. The goal is to guess the category that links a set of clues.
    
    Here are the clues revealed so far: {clues}
    The correct answer is: "{correct_answer}"
    
    I want to simulate a human playing who doesn't know the answer immediately.
    Generate 2 plausible but INCORRECT guesses that a human might make based on these clues.
    The guesses should be single words or short phrases.
    
    Return ONLY a JSON array of strings, e.g., ["guess1", "guess2"].
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Clean up code blocks if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("\n", 1)[0]
        
        guesses = json.loads(text)
        if isinstance(guesses, list):
            return guesses[:2] # Limit to 2 guesses
        return []
    except Exception as e:
        print(f"Error generating guesses with Gemini: {e}")
        return []
