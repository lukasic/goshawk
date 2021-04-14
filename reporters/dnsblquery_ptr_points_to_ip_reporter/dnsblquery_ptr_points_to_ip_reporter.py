# -*- coding: utf-8 -*-

#
# Validates if 2nd level domain from PTR record points to an IP address
# that belongs to spam network.
#

import json
import yaml
import re
from cachetools import TTLCache
import socket
import time
import sys
import argparse

from goshawk.reporter import RabbitmqConsumer, WorkerPool
from goshawk.client import GoshawkClient
from goshawk.config import config, setup

##
## Globals
##

goshawk = None 
blocklist_ip = None

cache_ip = TTLCache(maxsize=10000, ttl=1800)
cache_ptr = TTLCache(maxsize=10000, ttl=1800)

cache_reported = set()
queue_ip = list()


##
## Reporter Code
##

def check_name_reported(name):
    if name in cache_reported:
        return True

    result = goshawk.get_records(
        list_name=config['goshawk']['target_list'],
        value=name)['count'] > 0
    
    if result:
        cache_reported.add(name)

    return result


def report_name(d):
    if check_name_reported(d):
        print("Name %s already reported." % d)
        return

    print("Reporting name %s" % d)

    goshawk.post_record(
        reporter_name=config['goshawk']['reporter'],
        list_name=config['goshawk']['target_list'],
        value=d,
        reason='A "%s" points to reported server' % d
        )


def check_ip(ip):
    try:
        name, alias, addresslist = socket.gethostbyaddr(ip)

    except Exception as e:
        #print("gethostbyaddr:", ip, e)
        return

    if name in cache_ptr.keys():
        return

    if check_domain(name):
        scan_24_block(ip)

    cache_ptr[name] = 1


def check_domain(dom):
    print("Checking %s " % dom)
    ip = None
    try:
        tokens = dom.split('.')
        if "" in tokens: tokens.remove("")
        d = '.'.join(tokens[-2:])
    except:
        return

    for i in [d, "www." + d]:
        try:
            ip = socket.gethostbyname(d)
            if ip in blocklist_ip:
                report_name(d)
                return d
        except Exception as e:
            print(e)
            return


def scan_24_block(ip):
    print("Scan block: " + ip)
    net = ip.rsplit('.', 1)[0]
    for i in range(0, 256):
        bip = net + "." + str(i)
        print("Checking IP:", bip)

        try:
            name, alias, addresslist = socket.gethostbyaddr(bip)

        except Exception as e:
            #print("scan_24_block:error:", bip, e)
            continue
        
        check_domain(name)
        cache_ip[ip] = 1


is_running = True
def worker(id):
    while is_running:
        if len(queue_ip) == 0:
            time.sleep(1)
            continue

        ip = queue_ip.pop()
        check_ip(ip)


def callback(ch, method, properties, body):
  try:
    x = body.decode()
    if ' queries: client ' in x:
        data = json.loads(x)

        selector = data['message'].split()[7]
        if not selector.endswith(config['reporter']['dnsbl_name']):
            return

        # remove dnsbl name
        ip = selector[:-len(config['reporter']['dnsbl_name'])-1]
        # reverse IP order
        ip = ".".join(ip.split(".")[::-1])
        
        if ip in cache_ip.keys():
            return

        cache_ip[ip] = 1

        if len(queue_ip) > 50:
            time.sleep(1)
            print("queued items:", len(queue_ip))

        queue_ip.append(ip)

  except Exception as e:
    print(e)


def parse_argv():
    parser = argparse.ArgumentParser()

    parser.add_argument('--check-ip',
        dest='check_ip',
        default=False,
        help="Check one IP address and exit."
        )

    parser.add_argument('--config',
        dest='config',
        default="config.yml",
        help="Reporter config file.")

    return parser.parse_args(sys.argv[1:])


def init():
    global goshawk, blocklist_ip
    
    goshawk = GoshawkClient(
        config['goshawk']['api_url'])
    
    blocklist_ip = set(
        goshawk.get_records_values(list_name=config['goshawk']['source_list']))


def main():
    options = parse_argv()
    setup(options.config)
    print(config)
    init()

    if options.check_ip:
        check_ip(options.check_ip)
        sys.exit(0)

    workers = WorkerPool(
        target=worker,
        threads=config['reporter']['worker_threads'])
    
    workers.start()

    rmqconsumer = RabbitmqConsumer(
        amqp_uri=config['rabbitmq']['uri'],
        exchange=config['rabbitmq']['exchange'],
        routing_key=config['rabbitmq']['routing_key'],
        consumer_name_prefix=config['goshawk']['reporter'])

    rmqconsumer.consume(
        callback=callback)

    global is_running
    is_running = False
    workers.join()


if __name__ == "__main__":
    main()

