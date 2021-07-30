#!/usr/bin/env python3
# Copyright 2019 Northern.tech AS
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        https://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import logging
import time

from mender import common


logger = logging.getLogger("inventory")


class Inventory:
    _user_adm = None

    def __init__(self, email=None, password=None, server_url=None, user_adm=None):
        self._user_adm = user_adm

        if user_adm is None and (email and password and server_url):
            from mender import user_administration

            self._user_adm = user_administration.UserAdministration(
                email=self._email, password=self._password, server_url=self._server_url
            )
        if user_adm:
            self._user_adm = user_adm

    """
        + GET /devices
        + GET /devices?attr_name_1=foo& attr_name_2=100& ...
        + GET /devices/{id}
        + DELETE /devices/{id}
        + GET /devices/{id}/group
        + PUT /devices/{id}/group
        + DELETE /devices/{id}/group/{name}
        + GET /groups
        + GET /groups/{name}/devices
    """

    def get_devices(self, group=None, has_group=None, page=1, per_page=20, sort=None):
        # GET /devices
        return self._get_devices(
            page=page, per_page=per_page, group=group, has_group=has_group, sort=sort
        )

    def get_all_devices(self):
        # GET /devices
        _devices = []
        _page = 1
        while True:
            _start = time.time()
            _resp_json = self._get_devices(page=_page, per_page=500)
            if len(_resp_json) == 0 or not _resp_json:
                break
            for doc in _resp_json:
                _devices.append(doc)
            _end = time.time()
            logger.debug(
                "Page '%s' fetched for: '%s' sec" % (_page, round(_end - _start, 2))
            )
            _page += 1
        logger.debug("Devices count: %s" % len(_devices))
        return _devices

    def _get_devices(self, page, per_page, group=None, has_group=None, sort=None):
        # GET /devices
        _args = "?"
        if page is not None:
            _args += "&page=%s" % page
        if per_page is not None:
            _args += "&per_page=%s" % per_page
        if group is not None:
            _args += "&group=%s" % group
        if has_group is not None:
            _args += "&has_group=%s" % has_group
        if sort is not None:
            _args += "&sort=%s" % sort
        _url = "%s/api/management/v1/inventory/devices%s" % (
            self._user_adm.server_url,
            _args,
        )
        _params = {}
        return common.do_get_call(
            _url,
            status_code=200,
            params=_params,
            headers=self._user_adm.get_auth_header(),
        )

    def get_device(self, device_id):
        # GET /devices/{id}
        _url = "%s/api/management/v1/inventory/devices/%s" % (
            self._user_adm.server_url,
            device_id,
        )
        return common.do_get_call(
            _url, status_code=200, headers=self._user_adm.get_auth_header()
        )

    def get_devices_group(self, device_id):
        # GET /devices/{id}/group
        _url = "%s/api/management/v1/inventory/devices/%s/group" % (
            self._user_adm.server_url,
            device_id,
        )
        return common.do_get_call(
            _url, status_code=200, headers=self._user_adm.get_auth_header()
        )

    def get_groups(self):
        # GET /groups
        _url = "%s/api/management/v1/inventory/groups" % self._user_adm.server_url
        return common.do_get_call(
            _url, status_code=200, headers=self._user_adm.get_auth_header()
        )

    def get_groups_devices(self, group_name):
        # GET /groups/{name}/devices
        _url = "%s/api/management/v1/inventory/groups/%s/devices" % (
            self._user_adm.server_url,
            group_name,
        )
        return common.do_get_call(
            _url, status_code=200, headers=self._user_adm.get_auth_header()
        )

    def add_device_to_group(self, device_id, group_name):
        # PUT /devices/{id}/group
        _url = "%s/api/management/v1/inventory/devices/%s/group" % (
            self._user_adm.server_url,
            device_id,
        )
        _body = {"group": group_name}
        return common.do_put_call(
            _url, status_code=204, json=_body, headers=self._user_adm.get_auth_header()
        )

    def delete_device(self, device_id):
        # DELETE /devices/{id}
        _url = "%s/api/management/v1/inventory/devices/%s" % (
            self._user_adm.server_url,
            device_id,
        )
        return common.do_delete_call(
            _url, status_code=204, headers=self._user_adm.get_auth_header()
        )

    def delete_device_from_group(self, device_id, group_name):
        # DELETE /devices/{id}/group/{name}
        _url = "%s/api/management/v1/inventory/devices/%s/group/%s" % (
            self._user_adm.server_url,
            device_id,
            group_name,
        )
        return common.do_delete_call(
            _url, status_code=204, headers=self._user_adm.get_auth_header()
        )
