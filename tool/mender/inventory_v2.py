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

from mender import common


logger = logging.getLogger("inventory_v2")


class InventoryV2:
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

    def get_filters(self):
        # GET /filters
        _url = "%s/api/management/v2/inventory/filters?per_page=100" % (
            self._user_adm.server_url,
        )
        _params = {}
        return common.do_get_call(
            _url,
            status_code=200,
            params=_params,
            headers=self._user_adm.get_auth_header(),
        )

    def post_filter(self, filter):
        # POST /filters
        _url = "%s/api/management/v2/inventory/filters" % (self._user_adm.server_url,)
        common.do_post_call(
            _url, status_code=201, json=filter, headers=self._user_adm.get_auth_header()
        )

    def get_filter(self, filter_id):
        # GET /filters/{id}
        _url = "%s/api/management/v2/inventory/filters/%s" % (
            self._user_adm.server_url,
            filter_id,
        )
        return common.do_get_call(
            _url, status_code=200, headers=self._user_adm.get_auth_header()
        )

    def delete_filter(self, filter_id):
        # DELETE /filters/{id}
        _url = "%s/api/management/v2/inventory/filters/%s" % (
            self._user_adm.server_url,
            filter_id,
        )
        return common.do_delete_call(
            _url, status_code=204, headers=self._user_adm.get_auth_header()
        )
