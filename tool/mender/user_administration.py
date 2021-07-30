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

from requests.auth import HTTPBasicAuth

from mender import common


logger = logging.getLogger("user-administration")


class UserAdministration:
    _email = None
    _password = None
    server_url = None
    _auth_header = None

    def __init__(self, email=None, password=None, server_url=None):
        self._email = email
        self._password = password
        self.server_url = server_url

    """
        + POST /auth/login
        + POST /settings
        + GET /settings
        + POST /users
        + GET /users
        + GET /users/{id}
        + PUT /users/{id}
        + DELETE /users/{id}
    """

    def get_auth_header(self):
        # POST /auth/login
        if self._auth_header is not None:
            return self._auth_header
        _url = "%s/api/management/v1/useradm/auth/login" % self.server_url
        _token = common.do_post_call(
            _url,
            status_code=200,
            text=True,
            auth=HTTPBasicAuth(self._email, self._password),
        )
        if _token is None:
            logger.warning("Failed to fetch auth token.")
        self._auth_header = {"Authorization": "Bearer " + _token}
        logger.debug(
            "URL: '%s', user %s, authentication token: %s"
            % (self.server_url, self._email, self._auth_header)
        )
        return self._auth_header

    def update_user_settings(self, settings):
        # POST /settings
        _url = "%s/api/management/v1/useradm/settings" % self.server_url
        return common.do_post_call(
            _url, status_code=201, json=settings, headers=self.get_auth_header()
        )

    def get_user_settings(self):
        # GET /settings
        _url = "%s/api/management/v1/useradm/settings" % self.server_url
        return common.do_get_call(_url, headers=self.get_auth_header())

    def create_user(self, email, password):
        # POST /users
        _url = "%s/api/management/v1/useradm/users" % self.server_url
        _data = {"email": email, "password": password}
        return common.do_post_call(_url, json=_data, headers=self.get_auth_header())

    def get_users(self):
        # GET /users
        _url = "%s/api/management/v1/useradm/users" % self.server_url
        return common.do_get_call(_url, headers=self.get_auth_header())

    def get_user_information(self, user_id):
        # GET /users/{id}
        _url = "%s/api/management/v1/useradm/users/%s" % (self.server_url, user_id)
        return common.do_get_call(_url, headers=self.get_auth_header())

    # TODO: fix errors
    # getting 405 {"error":"Method not allowed"}
    def update_user_information(self, user_id, email=None, password=None):
        # PUT /users/{id}
        _url = "%s/api/management/v1/useradm/users/%s" % (self.server_url, user_id)
        _data = {}
        if email:
            _data["email"] = email
        if password:
            _data["password"] = password
        return common.do_put_call(
            _url, status_code=204, json=_data, headers=self.get_auth_header()
        )

    def delete_user(self, user_id):
        # DELETE /users/{id}
        _url = "%s/api/management/v1/useradm/users/%s" % (self.server_url, user_id)
        return common.do_delete_call(
            _url, status_code=204, headers=self.get_auth_header()
        )
