import redis

from teqbot import settings

CLIENT = redis.from_url(settings.REDIS_URL, db=0)
QUEUE = "teqbot"


def set(key, value, timeout=None):
    CLIENT.set(key, value, ex=timeout)


def get(key, default=None):
    return CLIENT.get(key) or default


def set_user_setting(key, value, timeout=None):
    set(f"{key}_{settings.MUMBLE_USER}", value, timeout)


def get_user_setting(key, default=None):
    return get(f"{key}_{settings.MUMBLE_USER}", default)
