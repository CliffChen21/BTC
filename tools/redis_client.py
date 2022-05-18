import pickle

import redis

r = redis.Redis(host='localhost', port=6379, db=0)


def SaveObj(obj):
    return pickle.dumps(obj)


def LoadObj(serials):
    return pickle.loads(serials)
