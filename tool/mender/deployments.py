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
import os

from mender import common


logger = logging.getLogger("deployments")


class Deployments:
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
        + POST /artifacts
        + GET /artifacts
        + GET /artifacts/{id}
        + PUT /artifacts/{id}
        + DELETE /artifacts/{id}
        + GET /artifacts/{id}/download
        + POST /deployments
        + GET /deployments
        + DELETE /deployments/devices/{id}
        + GET /deployments/releases
        + GET /deployments/{deployment_id}/devices
        + GET /deployments/{deployment_id}/devices/{device_id}/log
        + GET /deployments/{deployment_id}/statistics
        + PUT /deployments/{deployment_id}/status
        + GET /deployments/{id}
        + GET /limits/storage
    """

    def delete_artifact(self, artifact_id):
        # DELETE /artifacts/{id}
        _url = "%s/api/management/v1/deployments/artifacts/%s" % (
            self._user_adm.server_url,
            artifact_id,
        )
        return common.do_delete_call(
            _url, status_code=204, headers=self._user_adm.get_auth_header()
        )

    def delete_device_from_deployments(self, device_id):
        # DELETE /deployments/devices/{id}
        _url = "%s/api/management/v1/deployments/deployments/devices/%s" % (
            self._user_adm.server_url,
            device_id,
        )
        return common.do_delete_call(
            _url, status_code=204, headers=self._user_adm.get_auth_header()
        )

    # TODO: fix errors
    # copied from MenderAPI but fails with the following error
    # UnicodeDecodeError: 'utf-8' codec can't decode byte 0x8b in position 2561: invalid start byte
    def upload_artifact(self, artifact, description=None):
        # POST /artifacts
        _url = "%s/api/management/v1/deployments/artifacts" % self._user_adm.server_url
        _files = (
            ("description", (None, description)),
            ("size", (None, str(os.path.getsize(artifact)))),
            ("artifact", (artifact, open(artifact), "application/octet-stream")),
        )
        return common.do_post_call(
            _url,
            status_code=201,
            files=_files,
            headers=self._user_adm.get_auth_header(),
        )

    # TODO: fix errors
    # getting 405 {"Error":"Method not allowed"}
    def update_artifact(self, artifact_id, description):
        # PUT /artifacts/{id}
        _url = "%s/api/management/v1/deployments/artifacts/%s" % (
            self._user_adm.server_url,
            artifact_id,
        )
        _data = {"description": description}
        return common.do_put_call(
            _url, status_code=204, json=_data, headers=self._user_adm.get_auth_header()
        )

    def set_deployment_status(self, deployment_id, status):
        # PUT /deployments/{deployment_id}/status
        _url = "%s/api/management/v1/deployments/deployments/%s/status" % (
            self._user_adm.server_url,
            deployment_id,
        )
        _data = {"status": status}
        return common.do_put_call(
            _url, status_code=204, json=_data, headers=self._user_adm.get_auth_header()
        )

    def create_deployment(self, deployment_name, artifact_name, device_ids_list):
        # POST /deployments
        if not isinstance(device_ids_list, list):
            raise ValueError(
                "'list' is expected, but got '%s'" % str(type(device_ids_list))
            )
        _deployment = {
            "artifact_name": artifact_name,
            "name": deployment_name,
            "devices": device_ids_list,
        }
        _url = (
            "%s/api/management/v1/deployments/deployments" % self._user_adm.server_url
        )
        return common.do_post_call(
            _url,
            status_code=201,
            json=_deployment,
            headers=self._user_adm.get_auth_header(),
        )

    def get_deployment(self, deployment_id):
        # GET /deployments/{id}
        _url = "%s/api/management/v1/deployments/deployments/%s" % (
            self._user_adm.server_url,
            deployment_id,
        )
        return common.do_get_call(_url, headers=self._user_adm.get_auth_header())

    def get_deployments(self):
        # GET /deployments
        _url = (
            "%s/api/management/v1/deployments/deployments" % self._user_adm.server_url
        )
        return common.do_get_call(_url, headers=self._user_adm.get_auth_header())

    def get_artifact(self, artifact_id):
        # GET /artifacts/{id}
        _url = "%s/api/management/v1/deployments/artifacts/%s" % (
            self._user_adm.server_url,
            artifact_id,
        )
        return common.do_get_call(_url, headers=self._user_adm.get_auth_header())

    def get_artifacts(self):
        # GET /artifacts
        _url = "%s/api/management/v1/deployments/artifacts" % self._user_adm.server_url
        return common.do_get_call(_url, headers=self._user_adm.get_auth_header())

    def get_artifact_download_link(self, artifact_id):
        # GET /artifacts/{id}/download
        _url = "%s/api/management/v1/deployments/artifacts/%s/download" % (
            self._user_adm.server_url,
            artifact_id,
        )
        return common.do_get_call(_url, headers=self._user_adm.get_auth_header())

    def get_releases(self):
        # GET /deployments/releases
        _url = (
            "%s/api/management/v1/deployments/deployments/releases"
            % self._user_adm.server_url
        )
        return common.do_get_call(_url, headers=self._user_adm.get_auth_header())

    def get_deployment_devices(self, deployment_id):
        # GET /deployments/{deployment_id}/devices
        _url = "%s/api/management/v1/deployments/deployments/%s/devices" % (
            self._user_adm.server_url,
            deployment_id,
        )
        return common.do_get_call(_url, headers=self._user_adm.get_auth_header())

    def get_deployment_device_log(self, deployment_id, device_id):
        # GET /deployments/{deployment_id}/devices/{device_id}/log
        _url = "%s/api/management/v1/deployments/deployments/%s/devices/%s/log" % (
            self._user_adm.server_url,
            deployment_id,
            device_id,
        )
        return common.do_get_call(_url, headers=self._user_adm.get_auth_header())

    def get_deployment_statistics(self, deployment_id):
        # GET /deployments/{deployment_id}/statistics
        _url = "%s/api/management/v1/deployments/deployments/%s/statistics" % (
            self._user_adm.server_url,
            deployment_id,
        )
        return common.do_get_call(_url, headers=self._user_adm.get_auth_header())

    def get_storage_limit(self):
        # GET /limits/storage
        _url = (
            "%s/api/management/v1/deployments/limits/storage"
            % self._user_adm.server_url
        )
        return common.do_get_call(_url, headers=self._user_adm.get_auth_header())
