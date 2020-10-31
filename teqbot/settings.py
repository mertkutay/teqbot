from pathlib import Path

from environs import Env

ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent

env = Env()
env.read_env(ROOT_DIR / ".env")

VALID_COMMANDS = ["vol", "search", "url", "playlist", "skip", "stop", "cancel", "shuffle", "queue"]
MAX_FILES = 20

MUMBLE_HOST = env("MUMBLE_HOST")
MUMBLE_PORT = env.int("MUMBLE_PORT")
MUMBLE_USER = env("MUMBLE_USER")
MUMBLE_PASSWORD = env("MUMBLE_PASSWORD")

REDIS_HOST = env("REDIS_HOST")

DOWNLOAD_FOLDER = ROOT_DIR / "tmp"

SPOTIFY_CLIENT_ID = env("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = env("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REFRESH_TOKEN = env("SPOTIFY_REFRESH_TOKEN")
