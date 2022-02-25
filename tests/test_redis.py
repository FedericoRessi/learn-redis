import os

import pytest
import redis
import redis.lock


REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')


@pytest.fixture()
def redis_connection():
    return redis.from_url(url=REDIS_URL,
                          decode_responses=True)


def test_ping(redis_connection: redis.Redis):
    redis_connection.ping()


def test_set_get(redis_connection: redis.Redis):
    redis_connection.set('my_key', 'my_value')
    result = redis_connection.get('my_key')
    assert 'my_value' == result


@pytest.fixture()
def redis_lock(redis_connection: redis.Redis):
    redis_connection.delete('my_lock')
    lock = redis_connection.lock(name='my_lock',
                                 blocking_timeout=5.)
    yield lock
    redis_connection.delete('my_lock')


def test_lock_acquire(redis_lock: redis.lock.Lock):
    assert not redis_lock.owned()
    assert redis_lock.acquire()
    assert redis_lock.owned()
    assert not redis_lock.acquire(blocking=False)


def test_subscribe(redis_connection):
    pass
