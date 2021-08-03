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

import configargparse
import logging
import random

from math import ceil

import mender


devices_requested_pr_page = 500


def parse_config():
    parser = configargparse.ArgumentParser()
    parser.add_argument(
        "--username", type=str, required=True, env_var="USERNAME", help="Username"
    )
    parser.add_argument(
        "--password", type=str, required=True, env_var="PASSWORD", help="Password"
    )
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        env_var="URL",
        help="URL without protocol and slashes",
    )
    parser.add_argument(
        "--devices-qty",
        type=int,
        required=True,
        env_var="DEVICES_QTY",
        help="Devices quantity in group",
    )
    parser.add_argument(
        "--group-name",
        type=str,
        required=False,
        default=None,
        env_var="GROUP_NAME",
        help="Group name",
    )
    parser.add_argument(
        "--debug",
        type=bool,
        required=False,
        default=False,
        env_var="DEBUG",
        help="Enables debug logging",
    )
    return parser.parse_args()


# get all ungrouped devices
def get_ungrouped_devices(wanted_devices_in_group):
    pages = ceil(wanted_devices_in_group / devices_requested_pr_page)
    _devices = []
    for page in range(1, pages + 1):
        _result = mender.inventory.get_devices(
            page=page, per_page=devices_requested_pr_page, has_group=False
        )
        for _device in _result:
            if len(_devices) < wanted_devices_in_group:
                _devices.append(_device["id"])
            else:
                break
    # check if it's enough ungrouped devices to create a group with requested amount of devices in it
    if len(_devices) < wanted_devices_in_group:
        log.error(
            "It's %s devices available which is not enough to create group with %s devices in it."
            % (len(_devices), wanted_devices_in_group)
        )
        return None
    return _devices


# add devices into a group
def add_devices_to_group(devices, group_name):
    for device in devices:
        mender.inventory.add_device_to_group(device, group_name)

    log.info("'%s' devices added to group '%s'" % (len(devices), group_name))


if __name__ == "__main__":
    # parsing input params
    conf = parse_config()
    username = conf.username
    password = conf.password
    url = conf.url
    devices_qty = conf.devices_qty
    is_debug = conf.debug
    if conf.group_name is None:
        group_name = "group-%s" % random.randrange(100)
    else:
        group_name = conf.group_name

    # configuring logger
    logs_format = "[%(asctime)s] [%(levelname)-8s] %(message)s"
    if is_debug:
        logging.basicConfig(format=logs_format, level=logging.DEBUG)
    else:
        logging.basicConfig(format=logs_format, level=logging.INFO)
    log = logging.getLogger()

    # authenticate on the server
    mender.authenticate(email=username, password=password, server_url=url)

    # make a list of ungrouped devices with required qty
    devices = get_ungrouped_devices(devices_qty)
    if devices is None:
        exit(1)

    # add devices to a group
    add_devices_to_group(devices, group_name)
