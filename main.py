import argparse
import sys
import os
from api_client import fetch_daily_data, generate_plausible_guesses
from game_player import play_pinpoint
from video_producer import process_video
from uploader import upload_video

def main():
    parser = argparse.ArgumentParser(description="LinkedIn Pinpoint Automation")
    parser.add_argument("--dry-run", action="store_true", help="Skip upload step")
    args = parser.parse_args()

    print("=== Starting Daily LinkedIn Pinpoint Automation ===")

    # 1. Fetch Data
    print("\n--- Step 1: Fetching API Data ---")
    data = fetch_daily_data()
    if not data:
        print("Failed to fetch data. Exiting.")
        sys.exit(1)
    
    print(f"Target Answer: {data['answer']}")
    print(f"Clues: {data['clues']}")

    # 2. Enhance Data (Gemini Guesses)
    print("\n--- Step 2: Generating Plausible Guesses (Gemini) ---")
    guesses = generate_plausible_guesses(data['clues'], data['answer'])
    data['plausible_guesses'] = guesses
    print(f"Generated Guesses: {guesses}")

    # 3. Play & Record
    print("\n--- Step 3: Playing & Recording ---")
    raw_video = "gameplay_raw.webm"
    play_pinpoint(data, raw_video)
    
    if not os.path.exists(raw_video):
        print("Gameplay recording failed. Exiting.")
        sys.exit(1)

    # 4. Process Video
    print("\n--- Step 4: Editing Video ---")
    final_video = "final_output.mp4"
    success = process_video(raw_video, final_video)
    if not success:
        print("Video processing failed. Exiting.")
        sys.exit(1)

    # 5. Upload
    print("\n--- Step 5: Uploading ---")
    if args.dry_run:
        print("Dry run enabled. Skipping upload.")
        print(f"Final video saved to: {final_video}")
    else:
        upload_success = upload_video(final_video, data)
        if not upload_success:
            sys.exit(1)

    print("\n=== Automation Completed Successfully ===")

if __name__ == "__main__":
    main()
