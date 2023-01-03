import time


class MemCacheItem(object):
    def __init__(self, key, value, duration: int):
        self._key = key
        self._value = value
        self._expiry = time.time() + duration

    def value(self):
        return self.value()

    def expiry(self):
        return self._expiry

    def __repr__(self):
        return '<MemCacheItem {%s:%s} expires at: %s, expired: %s>' % (self._key, self._value, self.expiry(),
                                                                       self.expiry() < time.time())


class MemCache(dict):
    def __init__(self):
        dict.__init__(self)

    def get(self, key):
        if key not in self or self[key].expiry() > time.time():
            return None

        return self[key].value()

    def set(self, key, value, duration: int = 60):
        self[key] = MemCacheItem(key, value, duration)