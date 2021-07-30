#!/usr/bin/env python3

import logging
import os
import requests
import time

from random import randint


username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
base_url = os.getenv("URL")
deployment_name = os.getenv("DEPLOYMENT_NAME")
artifact_name = os.getenv("ARTIFACT_NAME")

logs_format = "[%(asctime)s] [%(levelname)-8s] %(message)s"
logging.basicConfig(format=logs_format, level=logging.INFO)
log = logging.getLogger()

# input validation
if deployment_name is None:
    deployment_name = "depl_name_" + str(randint(1000, 9999))
    log.warning("DEPLOYMENT_NAME is not set, using generated '%s'" % deployment_name)
if artifact_name is None:
    artifact_name = "test-update-1.0.0"
    log.warning("ARTIFACT_NAME is not set, using default '%s'" % artifact_name)
if username is None or password is None or base_url is None:
    log.error("ERROR: pass USERNAME, PASSWORD and URL environment variables")
    exit(1)

log.info("Starting creating deployment. USERNAME='%s', URL='%s'" % (username, base_url))
log.debug("trying to login.")

r = requests.post(
    "%s/api/management/v1/useradm/auth/login" % base_url,
    auth=(username, password),
    verify=False,
)
if r.status_code != 200:
    log.error("failed to login with %s:%s", username, password)
    exit(1)
token = r.text

devices = []

log.debug("getting devices list...")
page = 1
while True:
    start = time.time()
    url = (
        "%s/api/management/v2/devauth/devices?status=accepted&per_page=500&page=%s"
        % (base_url, page)
    )
    r = requests.get(url, headers={"Authorization": "Bearer " + token}, verify=False)

    if r.status_code != 200:
        print("Error: status code: %s, page: %s" % (r.status_code, page))
        exit(1)

    if len(r.json()) == 0:
        break

    for e in r.json():
        devices.append(e["id"])

    end = time.time()
    log.debug("page: %s time: %s sec" % (page, round(end - start, 2)))
    page += 1

log.debug("Accepted devices count: %s" % len(devices))

deployment = {
    "artifact_name": artifact_name,
    "name": deployment_name,
    "devices": devices,
}

url = "%s/api/management/v1/deployments/deployments" % base_url
r = requests.post(
    url, headers={"Authorization": "Bearer " + token}, json=deployment, verify=False
)

if r.status_code == 201:
    log.info(
        "Deployment successfully created: devices qty - %s, name - %s"
        % (len(devices), deployment_name)
    )
else:
    log.error(
        "Failed to create deployment. Status code: %s. Content: %s"
        % (r.status_code, r.text)
    )
    exit(1)
