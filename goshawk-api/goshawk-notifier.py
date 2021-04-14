# -*- coding: utf-8 -*-

import pika
import redis
import signal
import time
import json
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'goshawk.settings')

from django.conf import settings

params = pika.URLParameters(settings.AMQP_URI)
connection = pika.BlockingConnection(params)
channel = connection.channel()

redis = redis.Redis.from_url(settings.CACHES['notifier']['LOCATION'])

is_running = True
def stop(signal, frame):
    print("Caught signal. Stopping daemon...")
    global is_running
    is_running = False

signal.signal(signal.SIGINT, stop)
signal.signal(signal.SIGTERM, stop)

while is_running:
    # or use brpop("queue", 0) without signal handler
    msgid = redis.rpop("queue")
    if not msgid:
        time.sleep(0.1)
        continue
    
    msgid = msgid.decode()
    data = redis.get(msgid)
    redis.delete(msgid)
    event = json.loads(data)

    channel.basic_publish(
        exchange=event['exchange'],
        routing_key=event['routing_key'],
        body=json.dumps(event['record']))

redis.close()
channel.close()
connection.close()
