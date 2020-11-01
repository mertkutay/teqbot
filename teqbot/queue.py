import json
import random

import redis

from providers.youtube import YoutubeVideo
from teqbot import settings

CLIENT = redis.StrictRedis(host=settings.REDIS_HOST, port=6379, db=1)
QUEUE = "teqbot"


def push(video):
    video_str = json.dumps(video.to_dict())
    CLIENT.rpush(QUEUE, video_str)


def pop():
    video_str = CLIENT.lpop(QUEUE)
    if not video_str:
        return None

    video_dict = json.loads(video_str)
    return YoutubeVideo(**video_dict)


def get_lock(video_id):
    return CLIENT.lock(video_id)


def clear():
    CLIENT.delete(QUEUE)


def get_list():
    videos = []
    for entry in CLIENT.lrange(QUEUE, 0, -1):
        video_dict = json.loads(entry)
        videos.append(YoutubeVideo(**video_dict))
    return videos


def shuffle():
    queue_list = CLIENT.lrange(QUEUE, 0, -1)
    random.shuffle(queue_list)
    clear()
    CLIENT.rpush(QUEUE, *queue_list)


def next():
    video_str = CLIENT.lrange(QUEUE, 0, 1)
    if not video_str:
        return None

    video_dict = json.loads(video_str[0])
    return YoutubeVideo(**video_dict)
