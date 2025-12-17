import praw
import time
import random
from utils import check_if_seen

def get_reddit_client(config):
    return praw.Reddit(
        client_id=config["reddit_client_id"],
        client_secret=config["reddit_client_secret"],
        user_agent=config["reddit_user_agent"]
    )

def find_video_post(reddit, config):
    subreddits = config["subreddit_list"]
    # Randomly shuffle subreddits to not always pick from the first one
    random.shuffle(subreddits)
    
    for sub_name in subreddits:
        print(f"Suche in r/{sub_name}...")
        try:
            subreddit = reddit.subreddit(sub_name)
            
            sort_method = config.get("postSort", "top").lower()
            timeframe = config.get("postTimeframe", "day").lower()
            limit = 20 # Wie viele Posts überprüft werden sollen

            print(f"  Modus: {sort_method}, Zeitraum: {timeframe} (falls relevant)")

            if sort_method == "top":
                posts = subreddit.top(time_filter=timeframe, limit=limit)
            elif sort_method == "hot":
                posts = subreddit.hot(limit=limit)
            elif sort_method == "new":
                posts = subreddit.new(limit=limit)
            elif sort_method == "rising":
                posts = subreddit.rising(limit=limit)
            elif sort_method == "controversial":
                posts = subreddit.controversial(time_filter=timeframe, limit=limit)
            else:
                print(f"  Unbekannte Sortiermethode '{sort_method}', nutze 'hot'.")
                posts = subreddit.hot(limit=limit)

            for post in posts:
                # 0. Check History
                if check_if_seen(post.id):
                    print(f"  Überspringe {post.id} ({post.title}) - bereits bearbeitet.")
                    continue

                # 1. Check if it's a video generic check
                if not getattr(post, "is_video", False):
                    continue
                
                # Prüfe Dauer falls vorhanden
                duration = 0
                if hasattr(post, "media") and post.media:
                    reddit_video = post.media.get("reddit_video")
                    if reddit_video:
                        duration = reddit_video.get("duration", 0)
                
                # Filter nach Dauer (nur wenn Dauer bekannt ist)
                # Wir nehmen die Config Werte streng
                min_dur = config.get("min_duration_sec", 0)
                max_dur = config.get("max_duration_sec", 300)

                if duration > 0:
                    if duration < min_dur or duration > max_dur:
                        # Video zu kurz oder zu lang
                        continue

                # NSFW check
                if not config.get("allow_nsfw", False) and post.over_18:
                    continue

                print(f"  Gefunden: {post.title} (Dauer: {duration}s)")
                return post

        except Exception as e:
            print(f"Fehler beim Durchsuchen von {sub_name}: {e}")
            continue
    
    return None
