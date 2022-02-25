import os

import redis
import pytest


REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')


@pytest.fixture()
def redis_connection():
    return redis.from_url(url=REDIS_URL,
                          decode_responses=True)


def test_ping(redis_connection):
    redis_connection.ping()


def test_set_get(redis_connection):
    redis_connection.set('mykey', 'thevalueofmykey')
    result = redis_connection.get('mykey')
    assert 'thevalueofmykey' == result
