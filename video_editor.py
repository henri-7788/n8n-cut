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
    # Scale to fit width with margin
    max_content_width = target_width - (2 * margin)
    # Also considering height margin (e.g. for title)
    title_space = 200 # Space at top for title
    max_content_height = target_height - title_space - margin

    # Resize logic to FILL the available width (upscaling if necessary)
    # whilst keeping aspect ratio and staying within max height.
    
    current_w = reddit_clip.w
    current_h = reddit_clip.h
    
    # Calculate scale factors
    width_ratio = max_content_width / current_w
    height_ratio = max_content_height / current_h
    
    # Take the smaller ratio to ensure it fits both width and height constraints
    final_scale = min(width_ratio, height_ratio)
    
    # Apply resize
    print(f"  Original Video Size: {current_w}x{current_h}")
    print(f"  Target Max Size: {max_content_width}x{max_content_height}")
    print(f"  Scaling Factor: {final_scale:.2f}")
    
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

