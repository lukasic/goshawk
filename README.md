# Goshawk

Distributed system for building allow/block lists.

## Use cases

The main goal for now is to create framework for:

  * Building your own antispam DNSBL database
  * Brute-force attack blocking based on data from multiple servers

Concept of collections, lists and reporters can be used for building allowlist / blocklist of any type.

## Features

  * Ready for both IPv4 and IPv6
  * Realtime
  * Flexible and extensible
  * Agents works on older systems

## Components

  * postgresql - main database for goshawk-api
  * rabbitmq - messages and logs broker
  * goshawk-api - django based backend with rest api and simple web administration
  * agent - sends data (e.g. access logs from web server) to rabbitmq
  * reporter - analyzes data and adds / removes IP from specific list
  * subscriber - handles adding / removing blocked IP addresses on target system (e.g. manages nftables set on web server)



