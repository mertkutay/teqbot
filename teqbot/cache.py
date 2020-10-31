import redis

from teqbot import settings

CLIENT = redis.StrictRedis(host=settings.REDIS_HOST, port=6379, db=0)
QUEUE = "teqbot"


def set(key, value, timeout=None):
    CLIENT.set(key, value, ex=timeout)


def get(key, default=None):
    return CLIENT.get(key) or default
