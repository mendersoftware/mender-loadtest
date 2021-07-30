#!/usr/bin/env python3

import logging
import os
import sys

import mender

logs_format = "[%(asctime)s] [%(levelname)-8s] %(message)s"
logging.basicConfig(format=logs_format, level=logging.INFO)
log = logging.getLogger()

if len(sys.argv) == 1:
    log.error(
        "usage: USERNAME=<email> PASSWORD=<pwd> URL=<url> %s pending|accepted"
        % sys.argv[0]
    )
    exit(1)

status = sys.argv[1]
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
base_url = os.getenv("URL")

if username is None or password is None or base_url is None:
    log.error("ERROR: pass USERNAME, PASSWORD and URL environment variables")
    exit(1)
if status not in ("accepted", "pending"):
    log.error("usage: %s pending|accepted" % sys.argv[0])
    exit(1)


mender.authenticate(email=username, password=password, server_url=base_url)

devices_count = mender.dev_auth.get_devices_count(status=status)
print(devices_count)
