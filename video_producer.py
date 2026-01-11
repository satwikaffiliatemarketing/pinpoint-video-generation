import os
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip

def process_video(raw_video_path, output_path, intro_path="intro.mp4", outro_path="outro.mp4"):
    """
    Processes the raw gameplay video:
    - Adds intro and outro if they exist.
    - Converts to MP4 (if not already).
    """
    if not os.path.exists(raw_video_path):
        print(f"Error: Raw video {raw_video_path} not found.")
        return False

    try:
        clips = []
        
        # Add Intro
        if os.path.exists(intro_path):
            print("Adding intro...")
            clips.append(VideoFileClip(intro_path))
        else:
            print("No intro found, skipping.")

        # Add Gameplay
        print("Processing gameplay footage...")
        gameplay = VideoFileClip(raw_video_path)
        # Optional: Trim start/end if needed, or overlay text
        clips.append(gameplay)

        # Add Outro
        if os.path.exists(outro_path):
            print("Adding outro...")
            clips.append(VideoFileClip(outro_path))
        else:
            print("No outro found, skipping.")

        # Concatenate
        if len(clips) > 1:
            final_clip = concatenate_videoclips(clips, method="compose")
        else:
            final_clip = clips[0]

        # Write Output
        print(f"Writing final video to {output_path}...")
        final_clip.write_videofile(
            output_path, 
            codec="libx264", 
            audio_codec="aac", 
            fps=24,
            preset="medium",
            threads=4
        )
        
        # Cleanup
        for clip in clips:
            clip.close()
            
        return True

    except Exception as e:
        print(f"Error processing video: {e}")
        return False
