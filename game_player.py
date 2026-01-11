import time
import random
import asyncio
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError

GAME_URL = "https://www.linkedin.com/games/pinpoint"

def human_type(page: Page, selector: str, text: str):
    """Types text with random delays between keystrokes."""
    page.focus(selector)
    for char in text:
        page.keyboard.type(char)
        time.sleep(random.uniform(0.05, 0.15)) # Random delay 50ms - 150ms

def human_delay(min_seconds=2, max_seconds=5):
    """Random pause to simulate thinking."""
    time.sleep(random.uniform(min_seconds, max_seconds))

def play_pinpoint(data, output_video_path):
    """
    Plays the Pinpoint game using Playwright.
    Records the session to output_video_path.
    """
    answer = data["answer"]
    
    # We will receive guesses from the main loop logic, 
    # but strictly this function just executes the actions.
    # For simplicity, we'll take guesses as an argument or logic inside.
    # Let's import correct logic here or pass it in. 
    # To keep signatures clean, let's pass a list of guesses to try before the real one.
    
    guesses_to_try = data.get("plausible_guesses", [])
    
    with sync_playwright() as p:
        # Launch options for stealth and video
        browser = p.chromium.launch(
            headless=False, # Must be headless=False to actually record properly usually, or use xvfb on CI
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--no-sandbox"
            ]
        )
        
        # Context with video recording
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=".", # We'll move it later
            record_video_size={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="Asia/Kolkata" # User asked for Indian context logic, though mostly for Date. Browser location helps too.
        )
        
        # Stealth scripts
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        page = context.new_page()
        
        try:
            print(f"Navigating to {GAME_URL}...")
            page.goto(GAME_URL)
            human_delay(3, 5)

            # NOTE: The provided HTML showed an iframe. 
            # We need to ensure we are interacting with the game content.
            # Usually Playwright auto-pierces open shadow roots, but iframes need frame objects.
            # Let's check if there is an iframe.
            
            # Wait for game to load.
            # Look for common "Start" or "Play" buttons.
            # Based on standard Linkedin Games, there might be a "Play" button.
            
            # Heuristic selector for "Play" button
            try:
                play_button = page.get_by_text("Play", exact=True) or page.get_by_role("button", name="Play")
                if play_button.is_visible():
                    play_button.click()
                    human_delay(1, 2)
            except:
                print("No initial 'Play' button found, assuming game started or login required.")

            # Check if we need to login? 
            # The prompt implies a public game url, playing as guest.
            # If guest mode is behind a modal, we handle it.

            # The game interface usually has an input field.
            # We need to find the input.
            input_selector = "input[type='text']" # Generic fallback
            
            # Attempt 1-2: Wrong guesses
            for guess in guesses_to_try:
                print(f"Trying plausible guess: {guess}")
                try:
                    page.wait_for_selector(input_selector, timeout=5000)
                    human_type(page, input_selector, guess)
                    human_delay(0.5, 1)
                    page.keyboard.press("Enter")
                    human_delay(2, 4) # Wait for animation/feedback
                except Exception as e:
                    print(f"Could not enter guess '{guess}': {e}")
            
            # Final Attempt: Correct Answer
            print(f"Typing correct answer: {answer}")
            page.wait_for_selector(input_selector, timeout=5000)
            
            # Clear input if needed (usually entering a wrong guess clears it or requires manual clear)
            page.locator(input_selector).fill("") 
            
            human_type(page, input_selector, answer)
            human_delay(0.5, 1.5)
            page.keyboard.press("Enter")
            
            # Wait for Win Screen
            human_delay(5, 8) 
            print("Finished gameplay.")

        except Exception as e:
            print(f"Error during gameplay: {e}")
        finally:
            context.close() # Saves the video
            browser.close()
            
            # Rename the video file to the expected output path
            # context.close() saves the video to a random name in record_video_dir
            # We need to find it and rename it.
            import os
            import shutil
            
            # Find the latest .webm file (Playwright records to webm)
            files = [f for f in os.listdir(".") if f.endswith(".webm")]
            if files:
                latest_video = max(files, key=os.path.getctime)
                shutil.move(latest_video, output_video_path)
                print(f"Video saved to {output_video_path}")
            else:
                print("No video file found.")

# Usage example (commented out)
# play_pinpoint({"answer": "Apple", "plausible_guesses": ["Fruit", "Red"]}, "output.webm")
