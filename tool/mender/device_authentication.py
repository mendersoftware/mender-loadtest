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
import time

from requests_futures.sessions import FuturesSession

from mender import common


logger = logging.getLogger("device-authentication")


class DeviceAuthentication:
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
        + POST /devices
        + GET /devices
        + GET /devices/count
        + GET /devices/{id}
        + DELETE /devices/{id}
        + DELETE /devices/{id}/auth/{aid}
        + GET /devices/{id}/auth/{aid}/status
        + PUT /devices/{id}/auth/{aid}/status
        + GET /limits/max_devices
        + DELETE /tokens/{id}
    """

    def post_preauthorized_device(self, public_key, mac=None, sku=None, sn=None):
        # POST /devices
        _url = "%s/api/management/v2/devauth/devices" % self._user_adm.server_url
        _identity_data = {}
        if mac:
            _identity_data["mac"] = mac
        if sku:
            _identity_data["sku"] = sku
        if sn:
            _identity_data["sn"] = sn
        _body = {"identity_data": _identity_data, "pubkey": public_key}
        common.do_post_call(
            _url, status_code=201, json=_body, headers=self._user_adm.get_auth_header()
        )

    def delete_device(self, device_id):
        # DELETE /devices/{id}
        _url = "%s/api/management/v2/devauth/devices/%s" % (
            self._user_adm.server_url,
            device_id,
        )

        return common.do_delete_call(
            _url, status_code=204, headers=self._user_adm.get_auth_header()
        )

    def delete_all_devices(self, device_ids):
        # DELETE /devices/{id}
        with FuturesSession(max_workers=20) as session:
            for device_id in device_ids:
                session.delete(
                    url="%s/api/management/v2/devauth/devices/%s"
                    % (self._user_adm.server_url, device_id),
                    headers=self._user_adm.get_auth_header(),
                )

    def delete_device_auth_set(self, device_id, auth_set_id):
        # DELETE /devices/{id}/auth/{aid}
        _url = "%s/api/management/v2/devauth/devices/%s/auth/%s" % (
            self._user_adm.server_url,
            device_id,
            auth_set_id,
        )
        return common.do_delete_call(
            _url, status_code=204, headers=self._user_adm.get_auth_header()
        )

    def delete_device_token(self, token_id):
        # DELETE /tokens/{id}
        _url = "%s/api/management/v2/devauth/tokens/%s" % (
            self._user_adm.server_url,
            token_id,
        )
        return common.do_delete_call(
            _url, status_code=204, headers=self._user_adm.get_auth_header()
        )

    def get_device(self, device_id):
        # GET /devices/{id}
        if isinstance(device_id, str):
            _url = "%s/api/management/v2/devauth/devices/%s" % (
                self._user_adm.server_url,
                device_id,
            )
            return common.do_get_call(_url, headers=self._user_adm.get_auth_header())
        else:
            raise ValueError

    def get_devices(self, status, page=1, per_page=20):
        # GET /devices
        return self._get_devices(status=status, page=page, per_page=per_page)

    def get_all_devices(self, status):
        # GET /devices
        _devices = []
        _page = 1
        while True:
            _start = time.time()
            _resp_json = self._get_devices(status=status, page=_page, per_page=500)
            if not _resp_json:
                break
            if len(_resp_json) == 0:
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

    def _get_devices(self, status, page, per_page):
        # GET /devices
        _url = "%s/api/management/v2/devauth/devices?status=%s&per_page=%s&page=%s" % (
            self._user_adm.server_url,
            status,
            per_page,
            page,
        )
        return common.do_get_call(_url, headers=self._user_adm.get_auth_header())

    def get_devices_count(self, status=None):
        # GET /devices/count
        _url = "%s/api/management/v2/devauth/devices/count" % self._user_adm.server_url
        if status is not None:
            _url = "%s?status=%s" % (_url, status)
        data = common.do_get_call(_url, headers=self._user_adm.get_auth_header())
        return data.get("count") or 0

    def get_device_auth_set_status(self, device_id, auth_set_id):
        # GET /devices/{id}/auth/{aid}/status
        _url = "%s/api/management/v2/devauth/devices/%s/auth/%s/status" % (
            self._user_adm.server_url,
            device_id,
            auth_set_id,
        )
        return common.do_get_call(_url, headers=self._user_adm.get_auth_header())

    def get_devices_limit(self):
        # GET /limits/max_devices
        _url = (
            "%s/api/management/v2/devauth/limits/max_devices"
            % self._user_adm.server_url
        )
        return common.do_get_call(_url, headers=self._user_adm.get_auth_header())

    def update_device_auth_set_status(self, device_id, auth_set_id, status):
        # PUT /devices/{id}/auth/{aid}/status
        _url = "%s/api/management/v2/devauth/devices/%s/auth/%s/status" % (
            self._user_adm.server_url,
            device_id,
            auth_set_id,
        )
        return common.do_put_call(
            _url,
            status_code=204,
            json={"status": status},
            headers=self._user_adm.get_auth_header(),
        )

    def accept_devices(self, devices, sleep=0.1):
        # PUT /devices/{id}/auth/{aid}/status
        _count = 0
        _start = time.time()

        for device in devices:
            if len(device["auth_sets"]) > 1:
                logger.warning(
                    "Skipping device %s due to it has %d auth sets." % device,
                    len(device["auth_sets"]),
                )
                continue
            if len(device["auth_sets"]) == 0:
                logger.warning(
                    "Skipping device %s due to it has none auth sets." % device
                )
                continue

            self.update_device_auth_set_status(
                device["id"], device["auth_sets"][0]["id"], "accepted"
            )
            _count += 1
            time.sleep(sleep)

        _end = time.time()
        logger.debug(
            "Accepted '%s' devicesfrom '%s' for '%s' secs"
            % (_count, len(devices), round(_end - _start, 2))
        )
