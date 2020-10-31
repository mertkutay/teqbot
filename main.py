from threading import Thread

from teqbot import queue
from teqbot.bot import TeqBot


def main():
    bot = TeqBot()
    next_download = None
    play_thread = None
    while True:
        bot.video_in_queue.wait()

        current_video = queue.next()

        if not next_download:
            current_download = Thread(target=current_video.download, daemon=True)
            current_download.start()
        else:
            current_download = next_download

        if play_thread:
            play_thread.join()

        with bot.lock:
            next_video = queue.next()
            if not next_video or current_video.video_id != next_video.video_id:
                continue

        current_download.join()
        bot.send_message(f"Playing:<br>{current_video.title}")
        play_thread = Thread(target=bot.play, args=[current_video], daemon=True)
        play_thread.start()

        queue.pop()

        bot.recycle()

        with bot.lock:
            next_video = queue.next()
            if next_video:
                next_download = Thread(target=next_video.download, daemon=True)
                next_download.start()
            else:
                bot.video_in_queue.clear()
                next_download = None


if __name__ == "__main__":
    main()
