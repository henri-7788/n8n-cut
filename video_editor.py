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
    
    if reddit_clip.w > max_content_width:
        reddit_clip = reddit_clip.resize(width=max_content_width)
    
    # Position in center
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
        txt_clip = txt_clip.set_position(("center", 150)).set_duration(duration)
        
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

