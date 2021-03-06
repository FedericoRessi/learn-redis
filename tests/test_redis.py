import json
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


def test_pubsub(redis_connection: redis.Redis):
    pubsub = redis_connection.pubsub()
    pubsub.subscribe('my_channel')
    message = pubsub.get_message(timeout=5)
    assert message['channel'] == 'my_channel'
    assert message['type'] == 'subscribe'

    redis_connection.publish('my_channel', 'my_message')
    message = pubsub.get_message(timeout=5)
    assert message['channel'] == 'my_channel'
    assert message['type'] == 'message'
    assert message['data'] == 'my_message'


def test_stream(redis_connection: redis.Redis,
                stream='stream',
                group='group',
                consumer='consumer'):
    redis_connection.delete(stream, group, consumer)
    redis_connection.xadd(name=stream, fields={'message': 'hello!'})
    redis_connection.xgroup_create(name=stream, groupname=group, id='0-0')
    redis_connection.xgroup_createconsumer(name=stream, groupname=group,
                                           consumername=consumer)
    result = redis_connection.xreadgroup(groupname=group,
                                         consumername=consumer,
                                         streams={stream: '>'})
    print("")
    assert result != []
    for stream, messages in result:
        assert messages != []
        for message_id, message_data in messages:
            print(f"{message_id}: {message_data}")
            redis_connection.xack(stream, group, message_id)
