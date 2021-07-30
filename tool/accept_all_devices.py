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

import os
import logging
import mender
import threading

username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
base_url = os.getenv("URL")

logs_format = "[%(asctime)s] [%(levelname)-8s] %(message)s"
logging.basicConfig(format=logs_format, level=logging.INFO)
log = logging.getLogger()

# input validation
if username is None or password is None or base_url is None:
    log.error("pass USERNAME, PASSWORD and URL environment variables")
    exit(1)


if __name__ == "__main__":
    log.info(
        "Starting accepting all pending devices. USERNAME='%s', URL='%s'"
        % (username, base_url)
    )

    mender.authenticate(email=username, password=password, server_url=base_url)
    while True:
        devices = mender.dev_auth.get_devices(status="pending", per_page=50)
        if len(devices) == 0:
            break
        threads = []
        for device in devices:
            thread = threading.Thread(
                target=mender.dev_auth.accept_devices, args=([device],)
            )
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

    log.info("Finished accepting devices")
