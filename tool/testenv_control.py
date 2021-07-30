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
import json
import sys

import urllib3

urllib3.disable_warnings()

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


def create_all_filters():
    for mac_prefix in ["ff", "ee", "dd", "cc"]:
        # 4 groups of 12500 devices
        filter_group1_mac_prefix = {
            "name": "12.5k_group1_mac_" + mac_prefix,
            "terms": [
                {
                    "attribute": "device_group",
                    "scope": "inventory",
                    "type": "$eq",
                    "value": "group1",
                },
                {
                    "attribute": "mac",
                    "scope": "identity",
                    "type": "$regex",
                    "value": mac_prefix + ":00:00:.*",
                },
            ],
        }
        mender.inventory_v2.post_filter(filter_group1_mac_prefix)

    for mac_prefix in ["ff", "ee", "dd", "cc"]:
        # 4 groups of 25000 devices
        filter_group23_mac_prefix = {
            "name": "25k_group23_mac_" + mac_prefix,
            "terms": [
                {
                    "attribute": "device_group",
                    "scope": "inventory",
                    "type": "$in",
                    "value": ["group2", "group3"],
                },
                {
                    "attribute": "mac",
                    "scope": "identity",
                    "type": "$regex",
                    "value": mac_prefix + ":00:00:.*",
                },
            ],
        }
        mender.inventory_v2.post_filter(filter_group23_mac_prefix)

    for mac_prefix in ["bb", "aa", "99", "88"]:
        # 4 groups of 37500 devices
        filter_group23_mac_prefix = {
            "name": "37.5k_group23_mac_" + mac_prefix,
            "terms": [
                {
                    "attribute": "device_group",
                    "scope": "inventory",
                    "type": "$in",
                    "value": ["group1", "group2", "group3"],
                },
                {
                    "attribute": "mac",
                    "scope": "identity",
                    "type": "$regex",
                    "value": mac_prefix + ":00:00:.*",
                },
            ],
        }
        mender.inventory_v2.post_filter(filter_group23_mac_prefix)

    for mac_prefix in ["ff", "ee", "dd", "cc"]:
        # 4 groups of 50000 devices
        filter_group4567_mac_prefix = {
            "name": "50k_group4567_mac_" + mac_prefix,
            "terms": [
                {
                    "attribute": "device_group",
                    "scope": "inventory",
                    "type": "$in",
                    "value": ["group4", "group5", "group6", "group7"],
                },
                {
                    "attribute": "mac",
                    "scope": "identity",
                    "type": "$regex",
                    "value": mac_prefix + ":00:00:.*",
                },
            ],
        }
        mender.inventory_v2.post_filter(filter_group4567_mac_prefix)

    for mac_prefix in ["bb", "aa", "99", "88"]:
        # 4 groups of 75000 devices
        filter_group4567_mac_prefix = {
            "name": "75k_group4567_mac_" + mac_prefix,
            "terms": [
                {
                    "attribute": "device_group",
                    "scope": "inventory",
                    "type": "$in",
                    "value": [
                        "group4",
                        "group5",
                        "group6",
                        "group7",
                        "group8",
                        "group9",
                    ],
                },
                {
                    "attribute": "mac",
                    "scope": "identity",
                    "type": "$regex",
                    "value": mac_prefix + ":00:00:.*",
                },
            ],
        }
        mender.inventory_v2.post_filter(filter_group4567_mac_prefix)

    # 1 group of 100000 devices
    filter_group8_100k = {
        "name": "100k_group10",
        "terms": [
            {
                "attribute": "device_group",
                "scope": "inventory",
                "type": "$eq",
                "value": "group10",
            }
        ],
    }
    mender.inventory_v2.post_filter(filter_group8_100k)


def delete_all_filters():
    filters = mender.inventory_v2.get_filters()
    log.info("deleting %d filters" % len(filters))
    for f in filters:
        log.info("deleting %s" % json.dumps(f))
        mender.inventory_v2.delete_filter(f["id"])


def list_all_filters(details=False):
    filters = mender.inventory_v2.get_filters()
    if not filters:
        print("no filters")
        return
    log.info("listing %d filters" % len(filters))
    for f in filters:
        print(
            "%s %s %s" % (f["id"], f["name"], json.dumps(f["terms"]) if details else "")
        )


def do_main_filters():
    print("What do you want to do?")
    print("  L) List filters")
    print("  C) Create predefined filters")
    print("  D) Delete all filters")
    print("  Q) Quit")

    reply = ask("Choice? ")
    if reply.lower() == "q":
        return
    if reply.lower() == "l":
        list_all_filters()
    if reply.lower() == "c":
        create_all_filters()
    if reply.lower() == "d":
        delete_all_filters()


def list_all_deployments(details=False):
    deployments = mender.deployments.get_deployments()
    log.info("listing %d deployments" % len(deployments))
    print(
        "%36s %30s %15s %10s %10s" % ("id", "name", "status", "initial", "device_cnt")
    )
    for d in deployments:
        print(
            "%36s %30s %15s %10s %10s"
            % (
                d["id"],
                d["name"],
                d["status"],
                d["initial_device_count"],
                d["device_count"],
            )
        )


def create_new_deployment():
    filter_id = ask("Filter ID? ")
    deployment_name = ask("Deployment name? ")
    artifact_name = ask("Artifact name? ")
    deployment = {
        "name": deployment_name,
        "artifact_name": artifact_name,
        "filter_id": filter_id,
    }
    mender.deployments_v2.post_deployment(deployment)


def abort_deployment():
    deployment_id = ask("Deployment ID? ")
    mender.deployments.set_deployment_status(deployment_id, "aborted")


def do_main_deployments():
    print("What do you want to do?")
    print("  L) List deployments")
    print("  C) Create new deployment")
    print("  A) Abort deployment")
    print("  Q) Quit")

    reply = ask("Choice? ")
    if reply.lower() == "q":
        return
    if reply.lower() == "l":
        list_all_deployments()
    if reply.lower() == "c":
        create_new_deployment()
    if reply.lower() == "a":
        abort_deployment()


def ask(text):
    """Ask a question and return the reply."""

    sys.stdout.write(text)
    sys.stdout.flush()
    reply = sys.stdin.readline().strip()
    # Make a separator before next information chunk.
    sys.stdout.write("\n")
    return reply


def do_main():
    while True:
        print("-----------------------")
        print("What do you want to do?")
        print("  F) Filters list/create/delete")
        print("  D) Deployments list/create/abort")
        print("  Q) Quit")

        reply = ask("Choice? ")
        if reply.lower() == "q":
            return
        if reply.lower() == "f":
            do_main_filters()
        if reply.lower() == "d":
            do_main_deployments()


if __name__ == "__main__":
    mender.authenticate(email=username, password=password, server_url=base_url)
    do_main()
