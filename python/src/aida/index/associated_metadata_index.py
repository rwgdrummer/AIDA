# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================

from redis import Redis
from json import loads, dumps

class RedisMetaDataIndex:

    def _format_hash_prefix(self, hash_name):
        return "aida_imd_{}_".format(hash_name)

    def __init__(self,host):
        self.redis = Redis(host=host)
        if self.redis.get("aida_all_count") is None:
            self.redis.set("aida_all_count","0")


    def __setitem__(self, key, item):
        if self.redis.get(self._format_hash_prefix(key)) is None:
            self.redis.incr("aida_all_count")
        self.redis.set(self._format_hash_prefix(key), dumps(item))

    def __getitem__(self, key):
        v = self.redis.get(self._format_hash_prefix(key))
        return loads(v) if v else None

    def __repr__(self):
        return repr(self.__dict__)

    def __len__(self):
        return int(self.redis.get("aida_all_count"))

    def __delitem__(self, key):
        if self.redis.delete((self._format_hash_prefix(key))) > 0:
            self.redis.decr("aida_all_count")

    def clear(self):
        return None

    def copy(self):
        return None

    def has_key(self, key):
        return self.redis.get(self._format_hash_prefix(key))

    def update(self, *args, **kwargs):
        for k,v in kwargs.iteritems():
            self.__setitem__(k,v)

    def keys(self):
        return map(lambda x: x[9:-1],self.redis.keys(self._format_hash_prefix('*')))

    def values(self):
        return self.__dict__.values()

    def items(self):
        for k in self.redis.keys(self._format_hash_prefix('*')):
            yield k, self.redis.get(k)

    def pop(self, *args):
        for key in args:
            v = self.redis.get(self._format_hash_prefix(key))
            if v is not None:
                self.__delitem__(key)
                yield v

    def __cmp__(self, dict_):
        return self.__cmp__(self.__dict__, dict_)

    def __contains__(self, item):
        return self.has_key(item)

    def __iter__(self):
        return self.items()
