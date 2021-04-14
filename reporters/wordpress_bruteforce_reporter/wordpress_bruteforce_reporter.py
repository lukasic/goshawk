#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-

#
# Checks logs and counts POST requests on /xmlrpc.php and /wp-login.php url.
#

import json
import yaml
import re
from cachetools import TTLCache
import socket
import time
import sys
import argparse

from goshawk.reporter import RabbitmqConsumer
from goshawk.client import GoshawkClient
from goshawk.config import config, setup

## 
## Globals
## 

goshawk = None 

cache = TTLCache(maxsize=10000, ttl=600)
reported = TTLCache(maxsize=10000, ttl=60)


##
## Reporter Code
##

def check_ip_reported(ip):
    if ip in reported.keys():
        return True

    result = goshawk.get_records(
        list_name=config['goshawk']['list'],
        value=ip)['count'] > 0
    
    if result:
        reported[ip] = True

    return result


def block_ip(ip, data):
    if check_ip_reported(ip):
        print("IP %s already reported." % ip)
        return

    print("Reporting IP %s" % ip)

    goshawk.post_record(
        reporter_name=config['goshawk']['reporter'],
        list_name=config['goshawk']['list'],
        value=ip,
        reason=json.dumps(data))
    
    reported[ip] = True


def hit(ip, domain, attack_type):
    if ip not in cache.keys():
        cache[ip] = { 'count': 0, 'domains': dict() }
    if domain not in cache[ip]['domains'].keys():
        cache[ip]['domains'][domain] = dict()
    if attack_type not in cache[ip]['domains'][domain].keys():
        cache[ip]['domains'][domain][attack_type] = 0

    cache[ip]['domains'][domain][attack_type] += 1
    cache[ip]['count'] += 1

    if cache[ip]['count'] >= 20:
        #print("Blacklist:", ip, cache[ip])
        block_ip(ip, cache[ip])
        cache[ip]['count'] = 0


def process_log(log):
    tokens = log.split(" ")
    web = tokens[0].lower()
    ip = tokens[1]
    type = None
    if "xmlrpc.php" in log:
        type = "xmlrpc"
    elif "wp-login.php" in log:
        type = "wp-login"
    else:
        raise
    hit(ip, web, type)


def callback(ch, method, properties, body):
  try:
    x = body.decode()
    if "POST" not in x:
        return
    if "/xmlrpc.php" not in x and "/wp-login.php" not in x:
        return
    return process_log(x)

  except Exception as e:
    print(str(e))


def parse_argv():
    parser = argparse.ArgumentParser()

    parser.add_argument('--config',
        dest='config',
        default="config.yml",
        help="Reporter config file.")

    return parser.parse_args(sys.argv[1:])


def init():
    global goshawk
    
    goshawk = GoshawkClient(
        config['goshawk']['api_url'])


def main():
    options = parse_argv()
    setup(options.config)
    print(config)
    init()

    rmqconsumer = RabbitmqConsumer(
        amqp_uri=config['rabbitmq']['uri'],
        exchange=config['rabbitmq']['exchange'],
        routing_key=config['rabbitmq']['routing_key'],
        consumer_name_prefix=config['goshawk']['reporter'])

    rmqconsumer.consume(
        callback=callback)

if __name__ == "__main__":
    main()

