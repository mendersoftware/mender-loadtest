#!/usr/bin/env python3
# Copyright 2021 Northern.tech AS
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

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
