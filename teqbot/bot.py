import audioop
import base64
import io
import time
from threading import Event, Lock

import ffmpeg
import pymumble_py3 as pymumble

from providers.spotify import spotify_client
from providers.youtube import YoutubeVideo
from teqbot import cache, queue, settings


class TeqBot:
    def __init__(self):
        self.mumble = pymumble.Mumble(
            host=settings.MUMBLE_HOST,
            port=settings.MUMBLE_PORT,
            user=settings.MUMBLE_USER,
            password=settings.MUMBLE_PASSWORD,
            stereo=True,
        )
        self.mumble.callbacks.set_callback("text_received", self.on_message)
        self.mumble.set_codec_profile("audio")
        self.mumble.start()
        self.mumble.is_ready()

        self.channel = cache.get_user_setting("channel")
        if self.channel:
            try:
                self.mumble.channels.find_by_name(self.channel).move_in()
            except pymumble.errors.UnknownChannelError:
                self.send_message("Channel `{self.channel}` not found")
                self.channel = None
                cache.set_user_setting("channel", None)
        self.volume = cache.get_user_setting("volume", int, default=50)
        self.mumble.set_bandwidth(200000)
        self.lock = Lock()
        self.interrupt_event = Event()
        self.cancel_event = Event()
        self.video_in_queue = Event()
        if queue.next():
            self.video_in_queue.set()

    def send_message(self, text):
        channel = self.mumble.channels[self.mumble.users.myself["channel_id"]]
        channel.send_text_message(f"<br>{text}")

    def recycle(self):
        mp3_files = list(settings.DOWNLOAD_FOLDER.glob("*.mp3"))
        mp3_files.sort(key=lambda x: x.stat().st_atime, reverse=True)
        ids_to_keep = [mp3_file.name.split(".")[0] for mp3_file in mp3_files][
            : settings.MAX_FILES
        ]
        for file in list(settings.DOWNLOAD_FOLDER.glob("*")):
            if file.name.split(".")[0] not in ids_to_keep:
                file.unlink()

    def play(self, video):
        message = f"Playing:<br>{video.title}"
        thumbnail = video.thumbnail
        if thumbnail:
            buffer = io.BytesIO()
            thumbnail.save(buffer, format="JPEG")
            thumbnail_str = base64.b64encode(buffer.getvalue()).decode()
            message += f'<br><img - src="data:image/PNG;base64,{thumbnail_str}"/>'

        self.send_message(message)

        buffer_size = 1920
        process = (
            ffmpeg.input(video.file_path)
            .filter("loudnorm", i=-24)
            .output("pipe:", format="s16le", acodec="pcm_s16le", ac=2, ar="48k")
            .run_async(pipe_stdout=True)
        )
        while True:
            if self.interrupt_event.is_set():
                self.interrupt_event.clear()
                break

            while self.mumble.sound_output.get_buffer_size() > 0.1:
                time.sleep(0.01)
            raw = process.stdout.read(buffer_size)
            if not raw:
                break
            scaled = audioop.mul(raw, 2, self.volume / 100)
            self.mumble.sound_output.add_sound(scaled)

    def enqueue(self, video):
        if video.duration > settings.MAX_AUDIO_DURATION:
            self.send_message(f"Audio exceeds max duration limit:<br>{video.title}")

        with self.lock:
            queue.push(video)
            self.video_in_queue.set()

    def stop(self):
        with self.lock:
            self.send_message("Stopping")
            queue.clear()
            self.video_in_queue.clear()
            self.interrupt_event.set()

    def skip(self):
        with self.lock:
            self.send_message("Skipping")
            self.interrupt_event.set()

    def vol(self, level=None):
        if level:
            if level.isdigit():
                self.volume = min(int(level), 100)
            else:
                self.send_message("Invalid volume")
                return
        cache.set_user_setting("volume", self.volume)
        self.send_message(f"Volume: {self.volume}%")

    def search(self, query):
        result = YoutubeVideo.from_query(query)
        self.enqueue(result)

    def url(self, url):
        video = YoutubeVideo.from_url(url)
        self.enqueue(video)

    def shuffle(self):
        with self.lock:
            self.send_message("Shuffling")
            queue.shuffle()

    def playlist(self, url):
        songs = spotify_client.playlist_songs(url)
        for song in songs:
            time.sleep(0.01)
            if self.cancel_event.is_set():
                self.cancel_event.clear()
                break
            result = YoutubeVideo.from_query(song + " lyrics")
            self.enqueue(result)

    def cancel(self):
        self.cancel_event.set()

    def queue(self):
        message = "Queue:<br>"
        queue_list = queue.get_list()
        if queue_list:
            for i, video in enumerate(queue_list):
                message += f"{i+1}. {video.title}<br>"
        else:
            message += "Empty"
        self.send_message(message)

    def on_message(self, text):
        message = text.message.strip()
        if message[0] != "!":
            return

        tokens = message[1:].split(" ", 1)
        command = tokens[0]
        args = tokens[1:]

        if command in settings.VALID_COMMANDS:
            method = getattr(self, command)
            method(*args)
        else:
            self.send_message("Invalid command")
