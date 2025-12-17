import json
import os
import random

HISTORY_FILE = "downloaded_history.txt"

def load_config(path="config.json"):
    with open(path, "r") as f:
        return json.load(f)

def ensure_directories():
    dirs = ["backgrounds", "temp", "output"]
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
    return dirs

def get_random_background(bg_folder="backgrounds"):
    files = [f for f in os.listdir(bg_folder) if f.endswith(('.mp4', '.mov', '.mkv'))]
    if not files:
        raise FileNotFoundError("Keine Hintergrundvideos im Ordner 'backgrounds' gefunden!")
    return os.path.join(bg_folder, random.choice(files))

def cleanup_temp():
    folder = "temp"
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

# --- History / Deduplication Logic ---

def load_history():
    """Lädt die Liste bereits bearbeiteter Video-IDs."""
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

def save_to_history(post_id):
    """Speichert eine Video-ID in die History."""
    with open(HISTORY_FILE, "a") as f:
        f.write(f"{post_id}\n")
    print(f"Video {post_id} zur History hinzugefügt.")

def check_if_seen(post_id):
    history = load_history()
    return post_id in history
