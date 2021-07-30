#!/usr/bin/env python3

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
