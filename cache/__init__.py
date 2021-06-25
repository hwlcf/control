#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    __init__.py
    ~~~~~~~~~~~~~~~~~~~~~~~

    Defines different kinds of cache instances in this module.

"""
import redis
from redis.exceptions import LockError

from configs import RedisConf, AppConf

try:
    from redis.lock import LuaLock as Lock
except ImportError:
    from redis.lock import Lock


_r = redis.StrictRedis(
    host=RedisConf.HOST,
    port=RedisConf.PORT,
    password=RedisConf.PASSWORD,
    db=RedisConf.DB
)


class Cache(object):
    """缓存基类"""

    def __init__(self):
        self.cache = _r

    def key(self):
        """获取缓存key"""
        raise (NotImplementedError())


class BaseLock(Cache):
    """ 锁"""

    def __init__(self):
        super(BaseLock, self).__init__()
        self.cache = _r
        self.ok = False
        self.lock = None

    def acquire(self, expire, time_out=None):
        """
        请求锁
        :param expire: 过期时间. 过期时间一般可设置10s
        :param time_out: 超时时间. 如果为None，则超时时间等于expire时间.
            如果为0，则不阻塞. 该时间只算重试的睡眠时间，不计算请求缓存的时间
        :return ok:
            1: 加锁成功
            0: 锁已经存在
        """
        key = self.key()
        if time_out is None:
            time_out = expire

        # 防止重复获取锁
        if self.lock is not None and self.ok:
            return self.ok

        self.lock = self.cache.lock(
            key, timeout=expire, sleep=0.1, blocking_timeout=time_out,
            lock_class=Lock, thread_local=True
        )
        try:
            self.ok = self.lock.acquire()
        except LockError:
            self.ok = False

        return self.ok

    def release(self):
        """释放锁"""
        if self.lock is None or not self.ok:
            self.lock = None
            return False

        try:
            self.lock.release()
            self.lock = None
        except LockError:
            self.lock = None
            return False
        return True