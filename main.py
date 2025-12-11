import os
import sys
from utils import load_config, ensure_directories, get_random_background, cleanup_temp
from reddit_client import get_reddit_client, find_video_post
from downloader import download_video
from video_editor import process_video

def main():
    print("=== Reddit Video Automation ===")
    
    # 1. Setup
    ensure_directories()
    try:
        config = load_config()
    except FileNotFoundError:
        print("Fehler: config.json nicht gefunden.")
        return
    
    # 1b. Debug Config
    print(f"Config geladen. Sortierung: '{config.get('postSort')}', Zeitrahmen: '{config.get('postTimeframe')}'")
    print(f"Subreddits: {config.get('subreddit_list')}")

    # 2. Reddit Client
    try:
        reddit = get_reddit_client(config)
    except Exception as e:
        print(f"Fehler bei der Reddit-Verbindung: {e}")
        return

    # 3. Find Post
    print("Suche nach einem geeigneten Video...")
    post = find_video_post(reddit, config)
    
    if not post:
        print("Kein passendes Video gefunden, das den Kriterien entspricht.")
        return
    
    print(f"Gewähltes Video: {post.title}")
    
    # URL Logik verbessern um 403 Fehler zu vermeiden
    # Wir nehmen den direkten CDN Link anstatt des Post-Links
    download_url = post.url
    if hasattr(post, "media") and post.media and "reddit_video" in post.media:
        rv = post.media["reddit_video"]
        if rv.get("dash_url"):
            download_url = rv.get("dash_url")
            print("Nutze DASH URL (Beste Qualität + Audio)")
        elif rv.get("hls_url"):
            download_url = rv.get("hls_url")
            print("Nutze HLS URL")
        elif rv.get("fallback_url"):
            download_url = rv.get("fallback_url")
            print("Nutze Fallback URL (Eventuell ohne Audio)")
            
    print(f"URL für Download: {download_url}")
    
    # 4. Download Video
    print("Lade Video herunter...")
    video_path = download_video(download_url)
    
    if not video_path:
        print("Download fehlgeschlagen.")
        return
        
    # 5. Get Background
    try:
        bg_path = get_random_background()
        print(f"Hintergrundvideo: {os.path.basename(bg_path)}")
    except Exception as e:
        print(f"Fehler beim Laden des Hintergrunds: {e}")
        return

    # 6. Edit Video
    output_filename = f"final_{post.id}.mp4"
    output_path = os.path.join("output", output_filename)
    
    try:
        process_video(
            reddit_video_path=video_path,
            background_video_path=bg_path,
            title=post.title,
            config=config,
            output_path=output_path
        )
    except Exception as e:
        print(f"Fehler bei der Videobearbeitung: {e}")
        # import traceback
        # traceback.print_exc()

    # 7. Cleanup
    cleanup_temp()
    print("Fertig!")

if __name__ == "__main__":
    main()
