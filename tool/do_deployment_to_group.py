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
import requests

from random import randint


username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
base_url = os.getenv("URL")
deployment_name = os.getenv("DEPLOYMENT_NAME")
group_name = os.getenv("GROUP_NAME")
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
if username is None or password is None or base_url is None or group_name is None:
    log.error(
        "ERROR: pass USERNAME, PASSWORD, URL and GROUP_NAME environment variables"
    )
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

deployment = {
    "artifact_name": artifact_name,
    "name": deployment_name,
    "group": group_name,
}

url = "%s/api/management/v1/deployments/deployments/group/%s" % (base_url, group_name)
r = requests.post(
    url, headers={"Authorization": "Bearer " + token}, json=deployment, verify=False
)

if r.status_code == 201:
    log.info(
        "Deployment successfully created: group - %s, name - %s"
        % (group_name, deployment_name)
    )
else:
    log.error(
        "Failed to create deployment. Status code: %s. Content: %s"
        % (r.status_code, r.text)
    )
    exit(1)
