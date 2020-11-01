import re
import time
from functools import wraps

import youtube_dlc
from PIL import Image

from teqbot import settings


def retry(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except:  # noqa
            time.sleep(0.5)
            return function(*args, **kwargs)

    return wrapper


class YoutubeVideo:
    def __init__(self, video_id, **kwargs):
        self.video_id = video_id
        self.url = self.get_video_url(video_id)

        self.title = kwargs.get("title")
        self.duration = kwargs.get("duration")
        if not all([self.title, self.duration]):
            self.get_info()

    @retry
    def get_info(self):
        with youtube_dlc.YoutubeDL(dict(noplaylist=True)) as ydl:
            info = ydl.extract_info(self.url, download=False)

        self.title = info["title"]
        self.duration = info["duration"]

    @staticmethod
    def get_video_id(url):
        return re.search(r"youtube.com/watch?v=(.+)").group(1)

    @staticmethod
    def get_video_url(video_id):
        return f"https://www.youtube.com/watch?v={video_id}"

    @classmethod
    @retry
    def from_query(cls, query):
        with youtube_dlc.YoutubeDL(dict(noplaylist=True)) as ydl:
            info = ydl.extract_info(f"ytsearch: {query}", download=False)
            return cls(video_id=info["entries"][0]["id"])

    @classmethod
    def from_url(cls, url):
        return cls(video_id=cls.get_video_id(url))

    @property
    def file_path(self):
        return settings.DOWNLOAD_FOLDER / f"{self.video_id}.mp3"

    @property
    def downloaded(self):
        return self.file_path.exists()

    @property
    def thumbnail(self):
        thumbnail_path = settings.DOWNLOAD_FOLDER / f"{self.video_id}.jpg"
        if not thumbnail_path.exists():
            thumbnail_path = settings.DOWNLOAD_FOLDER / f"{self.video_id}.webp"
            if not thumbnail_path.exists():
                return None
        img = Image.open(thumbnail_path)
        img.thumbnail((100, 100), Image.ANTIALIAS)
        return img

    @retry
    def download(self):
        if self.downloaded:
            return self.file_path

        out_template = str(self.file_path).replace(".mp3", ".%(ext)s")
        params = {
            "format": "bestaudio/best",
            "outtmpl": out_template,
            "noplaylist": True,
            "writethumbnail": True,
            "updatetime": False,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                },
                {"key": "FFmpegMetadata"},
            ],
        }
        with youtube_dlc.YoutubeDL(params) as ydl:
            ydl.extract_info(self.url)

        return self.file_path

    def to_dict(self):
        return {
            "video_id": self.video_id,
            "title": self.title,
            "duration": self.duration,
        }
