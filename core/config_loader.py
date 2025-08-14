import os
from dotenv import load_dotenv, set_key
from pathlib import Path
from yt_dlp import YoutubeDL

load_dotenv()

# 🔐 Variables d’environnement
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
APPLICATION_ID = os.getenv('DISCORD_APPLICATION_ID')
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
TWITCH_ACCESS_TOKEN = os.getenv("TWITCH_ACCESS_TOKEN")
TWITCH_API_URL = os.getenv("TWITCH_API_URL")

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

# 🔊 YouTube DL
YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto"
}
ytdl = YoutubeDL(YTDL_OPTIONS)

# 🔧 FFMPEG Config
FFMPEG_PATH = os.getenv("FFMPEG_PATH") or r"C:\ffmpeg\bin\ffmpeg.exe"
FFMPEG_OPTIONS = {
    "options": "-vn",
    "executable": FFMPEG_PATH
}

# 🔁 Rafraîchir token Twitch
env_path = Path(".env")
set_key(str(env_path), "TWITCH_ACCESS_TOKEN", TWITCH_ACCESS_TOKEN)