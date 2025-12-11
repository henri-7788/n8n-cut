import yt_dlp
import os

def download_video(post_url, output_folder="temp"):
    """
    Downloads the video from the given Reddit post URL.
    Returns the path to the downloaded video file.
    """
    
    output_template = os.path.join(output_folder, 'reddit_video.%(ext)s')
    
    ydl_opts = {
        'outtmpl': output_template,
        'format': 'bestvideo+bestaudio/best',  # Merge video and audio
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([post_url])
            
        # Check what file was created. It should be mp4 because of merge_output_format
        expected_path = os.path.join(output_folder, 'reddit_video.mp4')
        if os.path.exists(expected_path):
            return expected_path
        
        # Fallback if filename differs
        for file in os.listdir(output_folder):
            if file.startswith("reddit_video"):
                return os.path.join(output_folder, file)
                
    except Exception as e:
        print(f"Fehler beim Download: {e}")
        return None
