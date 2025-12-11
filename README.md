# Reddit Video Automation

Ein automatisiertes Python-Tool, das Videos von Reddit herunterlädt, diese auf ein zufälliges Hintergrundvideo schneidet (z.B. Gameplay oder Naturaufnahmen) und den Titel des Posts als Overlay hinzufügt. Optimiert für die Erstellung von Content für TikTok, Reels oder Shorts.

## Funktionen

*   🔍 **Automatisierte Suche**: Durchsucht konfigurierbare Subreddits nach Videos basierend auf Sortierung (Top, Hot, Rising, etc.) und Zeitrahmen.
*   📥 **Download**: Lädt Video und Audio von Reddit in bester Qualität herunter.
*   🎬 **Videobearbeitung**: 
    *   Kombiniert das Reddit-Video mit einem zufälligen Hintergrund aus einem lokalen Ordner.
    *   Passt das Format auf 9:16 (Hochformat) an.
    *   Zentriert das Reddit-Video.
    *   Fügt den Post-Titel als Text-Overlay hinzu.
*   ⚙️ **Voll Konfigurierbar**: Alle Parameter (Subreddits, Videolänge, Sortierung) sind über eine `config.json` steuerbar.

## Voraussetzungen

Das Projekt ist für die Ausführung auf **Ubuntu / Linux** optimiert, läuft aber auch auf Windows/Mac.

### System-Abhängigkeiten (Ubuntu)

Das Tool benötigt `ffmpeg` für die Videobearbeitung und `imagemagick` für die Texterstellung.

```bash
sudo apt update
sudo apt install ffmpeg imagemagick
```

**Wichtig für ImageMagick:**
Standardmäßig deaktiviert Ubuntu oft Text-Operationen in ImageMagick aus Sicherheitsgründen. Du musst dies möglicherweise in der `policy.xml` anpassen:
1. Öffne `/etc/ImageMagick-6/policy.xml` (Pfad kann je nach Version variieren).
2. Suche nach `<policy domain="path" rights="none" pattern="@*" />`.
3. Ändere es zu `<policy domain="path" rights="read|write" pattern="@*" />` oder kommentiere die Zeile aus.

### Python Abhängigkeiten

Installiere die benötigten Python-Pakete:

```bash
pip install -r requirements.txt
```

Inhalt der `requirements.txt`:
*   `praw` (Reddit API)
*   `moviepy` (Videobearbeitung)
*   `yt-dlp` (Video Download)
*   `requests`

## Einrichtung

1.  **Reddit API Credentials**:
    Du benötigst einen Reddit Script Account. Trage `client_id` und `client_secret` in die `config.json` ein.
    
2.  **Hintergrundvideos**:
    Erstelle einen Ordner namens `backgrounds` im Projektverzeichnis und lege dort deine MP4-Dateien ab (z.B. Minecraft Parkour, Naturvideos, GTA Gameplay). Das Skript wählt zufällig eines aus.

## Konfiguration (`config.json`)

Die Datei `config.json` steuert das Verhalten des Bots. Änderungen werden bei jedem Neustart des Skripts übernommen.

```json
{
  "reddit_client_id": "DEINE_ID",
  "reddit_client_secret": "DEIN_SECRET",
  "reddit_user_agent": "DeinUserAgent",
  "subreddit_list": ["nextfuckinglevel", "videos", "beamazed"],
  "min_duration_sec": 10,
  "max_duration_sec": 60,
  "video_width": 1080,
  "video_height": 1920,
  "allow_nsfw": false,
  "postSort": "top",       // Optionen: hot, top, new, rising, controversial
  "postTimeframe": "day",  // Optionen: hour, day, week, month, year, all (nur für top/controversial)
  "target_platforms": ["tiktok", "reels"]
}
```

## Nutzung

Führe das Hauptskript aus:

```bash
python3 main.py
```

Der Ablauf ist vollautomatisch:
1.  Config wird geladen.
2.  Suche nach passendem Video auf Reddit.
3.  Download des Videos.
4.  Wahl eines zufälligen Hintergrunds.
5.  Rendern des finalen Videos in den Ordner `output/`.
6.  Bereinigung temporärer Dateien.

## Projektstruktur

```
.
├── backgrounds/      # Hier deine Hintergrundvideos ablegen
├── output/           # Hier landen die fertigen Videos
├── temp/             # Temporäre Dateien (werden automatisch gelöscht)
├── config.json       # Konfigurationsdatei
├── main.py           # Hauptprogramm
├── reddit_client.py  # Reddit Such-Logik
├── downloader.py     # Download Logik (yt-dlp)
├── video_editor.py   # Schnitt und Bearbeitung (MoviePy)
├── utils.py          # Hilfsfunktionen
└── requirements.txt  # Python Abhängigkeiten
```
