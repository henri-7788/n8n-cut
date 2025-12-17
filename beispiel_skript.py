import os
import configparser
import logging
import shutil
import youtube_dl  # neuer Import
import praw

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Lade Konfiguration
config = configparser.ConfigParser()
config.read("/home/zotac/Schreibtisch/reddit_WTF/config.ini")

CLIENT_ID = config["reddit"]["client_id"]
CLIENT_SECRET = config["reddit"]["client_secret"]
USER_AGENT = config["reddit"]["user_agent"]
SUBREDDIT_NAME = config["reddit"]["subreddit"]
TIME_FILTER = config["settings"].get("time_filter", "day")

# Erstelle Ordner für Downloads, falls nicht vorhanden
DOWNLOAD_DIR = "/home/zotac/Schreibtisch/reddit_WTF/downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Datei für bereits heruntergeladene IDs
DOWNLOADED_IDS_FILE = "/home/zotac/Schreibtisch/reddit_WTF/downloaded_ids.txt"
if not os.path.exists(DOWNLOADED_IDS_FILE):
    with open(DOWNLOADED_IDS_FILE, "w") as f:
        pass

def load_downloaded_ids():
    with open(DOWNLOADED_IDS_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

downloaded_ids = load_downloaded_ids()

def save_downloaded_id(post_id):
    with open(DOWNLOADED_IDS_FILE, "a") as f:
        f.write(post_id + "\n")

def save_caption(post):
    caption = post.title
    caption_file = os.path.join(DOWNLOAD_DIR, f"{post.id}.txt")
    try:
        with open(caption_file, "w", encoding="utf-8") as f:
            f.write(caption)
        logging.info(f"Caption für Post {post.id} wurde in {caption_file} gespeichert.")
    except Exception as e:
        logging.error(f"Fehler beim Speichern der Caption für Post {post.id}: {e}")

# Initialisiere Reddit API via PRAW
reddit = praw.Reddit(client_id=CLIENT_ID,
                     client_secret=CLIENT_SECRET,
                     user_agent=USER_AGENT)

# Funktion zum Herunterladen des Videos mit Ton
def download_video(url, output_path):
    ydl_opts = {
        'outtmpl': output_path,
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'
        }]
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        logging.error(f"Fehler beim Herunterladen von {url}: {e}")
        return False

def process_post(post):
    # Überspringe den Post, falls bereits heruntergeladen
    if post.id in downloaded_ids:
        logging.info(f"Post {post.id} wurde bereits gerippt.")
        return False

    video_url = None
    filename = None

    # Prüfe, ob es sich um ein Reddit-Video handelt
    if post.is_video and post.media and "reddit_video" in post.media:
        video_url = post.media["reddit_video"].get("fallback_url")
        filename = f"{post.id}.mp4"
    else:
        logging.info(f"Post {post.id} enthält kein unterstütztes Video.")
        return False

    file_path = os.path.join(DOWNLOAD_DIR, filename)
    logging.info(f"Lade {post.id} von {video_url} herunter...")

    if not download_video(video_url, file_path):
        logging.error(f"Download von {post.id} fehlgeschlagen.")
        return False

    logging.info(f"Post {post.id} wurde erfolgreich heruntergeladen.")

    # Speichere die Caption in einer TXT-Datei
    save_caption(post)
    
    # Speichere die Post-ID, um Doppel-Downloads zu vermeiden
    save_downloaded_id(post.id)
    return True

def main():
    subreddit = reddit.subreddit(SUBREDDIT_NAME)
    logging.info(f"Verarbeite Top-Post aus r/{SUBREDDIT_NAME} (Timefilter: {TIME_FILTER})")

    # Durchlaufe Top-Posts und breche nach dem ersten erfolgreichen Download ab
    for post in subreddit.top(time_filter=TIME_FILTER, limit=50):
        if process_post(post):
            logging.info("Erfolgreich ein Video heruntergeladen. Beende das Skript.")
            break

if __name__ == "__main__":
    main()
