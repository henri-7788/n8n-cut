# Fix für Inkompatibilität zwischen MoviePy 1.0.3 und Pillow 10+
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, vfx

import os

def process_video(reddit_video_path, background_video_path, title, config, output_path="output/final_video.mp4"):
    print("Starte Videobearbeitung...")
    
    # Config values
    target_width = config.get("video_width", 1080)
    target_height = config.get("video_height", 1920)
    margin = config.get("video_margin_px", 20)
    
    # Load clips
    reddit_clip = VideoFileClip(reddit_video_path)
    bg_clip = VideoFileClip(background_video_path)
    
    duration = reddit_clip.duration
    
    # Prepare Background
    # Loop background if it's too short
    if bg_clip.duration < duration:
        bg_clip = bg_clip.loop(duration=duration)
    else:
        bg_clip = bg_clip.subclip(0, duration)
        
    # Resize/Crop Background to fill screen
    bg_ratio = bg_clip.w / bg_clip.h
    target_ratio = target_width / target_height
    
    if bg_ratio > target_ratio:
        # Background is wider than target, crop width
        new_width = int(bg_clip.h * target_ratio)
        bg_clip = bg_clip.crop(x1=(bg_clip.w - new_width) / 2, width=new_width, height=bg_clip.h)
    else:
        # Background is taller/same, crop height
        new_height = int(bg_clip.w / target_ratio)
        bg_clip = bg_clip.crop(y1=(bg_clip.h - new_height) / 2, height=new_height, width=bg_clip.w)
        
    bg_clip = bg_clip.resize((target_width, target_height))
    
    # Prepare Reddit Clip (Center)
    
    # 1. Calculate Max Dimensions based on Config Margin
    # We enforce the margin strictly.
    max_content_width = target_width - (2 * margin)
    
    # For height, we just respect the vertical margin (no extra space for title reserved anymore)
    # This allows 9:16 videos to fill the screen almost completely.
    max_content_height = target_height - (2 * margin)

    # 2. Resize Logic (Fill Width primarily)
    # Goal: Make the video as wide as possible (up to max_content_width)
    # provided it doesn't exceed max_content_height.
    
    current_w = reddit_clip.w
    current_h = reddit_clip.h
    
    # Calculate scale needed to match MAX WIDTH
    scale_to_fit_width = max_content_width / current_w
    
    # Calculate resulting height if we scale to fit width
    new_height_if_fit_width = current_h * scale_to_fit_width
    
    if new_height_if_fit_width <= max_content_height:
        # Perfect! We can fill the width and still fit in height.
        final_scale = scale_to_fit_width
    else:
        # If filling width makes it too tall, we must limit by height
        # This will result in larger side margins, but that's geometrically unavoidable 
        # without cropping (and we don't want to crop the Reddit video content).
        print("  Info: Video ist zu hoch für die Breite (Super-V-Format?), skaliere nach Höhe.")
        scale_to_fit_height = max_content_height / current_h
        final_scale = scale_to_fit_height
    
    # Apply resize
    print(f"  Original: {current_w}x{current_h}")
    print(f"  Ziel-Breite (aus Config): {max_content_width}px (Margin: {margin}px)")
    print(f"  Skalierungsfaktor: {final_scale:.3f}")
    
    reddit_clip = reddit_clip.resize(final_scale)

    # Force position to center
    reddit_clip = reddit_clip.set_position(("center", "center"))
    
    # Prepare Title
    # Use TextClip. Notes: On Linux requires ImageMagick.
    # We wrap text to fit width
    # Heuristic for font size: 4% of height?
    font_size = 50 
    
    # Clean title helps avoids issues
    clean_title = title.strip()
    
    try:
        # Attempt to create text clip
        # method='caption' automatically wraps text in provided size
        txt_clip = TextClip(
            clean_title, 
            fontsize=font_size, 
            color='white', 
            stroke_color='black', 
            stroke_width=2,
            font='Arial-Bold', 
            method='caption',
            size=(target_width - 2*margin, None), # Auto height
            align='center'
        )
        # Position user mentions "top", but not covering video if possible. 
        # Ideally: Top margin.
        txt_clip = txt_clip.set_position(("center", 100)).set_duration(duration) # Slightly higher

        
    except Exception as e:
        print(f"Warnung: TextClip konnte nicht erstellt werden (ImageMagick fehlt vielleicht?): {e}")
        txt_clip = None

    # Composite
    clips_to_compose = [bg_clip, reddit_clip]
    if txt_clip:
        clips_to_compose.append(txt_clip)
        
    final = CompositeVideoClip(clips_to_compose, size=(target_width, target_height))
    
    # Write output
    final.write_videofile(
        output_path, 
        codec='libx264', 
        audio_codec='aac', 
        fps=30,
        threads=4
    )
    
    # Cleanup
    reddit_clip.close()
    bg_clip.close()
    final.close()
    print(f"Video gespeichert unter: {output_path}")

