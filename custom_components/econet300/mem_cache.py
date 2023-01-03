import logging
import time

_LOGGER = logging.getLogger(__name__)

class MemCacheItem:
    def __init__(self, key, value, duration: int):
        self._key = key
        self._value = value
        self._expiry = time.time() + duration

    def value(self):
        return self._value

    def expiry(self):
        return self._expiry

    def __repr__(self):
        return '<MemCacheItem {%s:%s} expires at: %s, expired: %s>' % (self._key, self._value, self.expiry(),
                                                                       self.expiry() < time.time())


class MemCache:
    def __init__(self):
        self._data = dict()

    def exists(self, key):
        return self.get(key) is not None

    def get(self, key):
        if key not in self._data or self._data[key].expiry() < time.time():
            _LOGGER.debug("Cache missing for: '{}'".format(key))
            return None

        return self._data[key].value()

    def set(self, key, value, duration: int = 60):
        _LOGGER.debug("Caching value for: '{}'".format(key))
        self._data[key] = MemCacheItem(key, value, duration)
