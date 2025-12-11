import json
import os
import random

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
