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

from mender import device_authentication
from mender import user_administration
from mender import inventory as inventory_lib
from mender import inventory_v2 as inventory_v2_lib
from mender import deployments as deployments_lib
from mender import deployments_v2 as deployments_v2_lib


user_adm = None
dev_auth = None
deployments = None
deployments_v2 = None
inventory = None
inventory_v2 = None


def _init(
    email=os.getenv("MENDER_USERNAME"),
    password=os.getenv("MENDER_PASSWORD"),
    server_url=os.getenv("MENDER_SERVER_URL"),
):
    global user_adm
    global dev_auth
    global deployments
    global deployments_v2
    global inventory
    global inventory_v2
    user_adm = user_administration.UserAdministration(
        email=email, password=password, server_url=server_url
    )
    dev_auth = device_authentication.DeviceAuthentication(user_adm=user_adm)
    deployments = deployments_lib.Deployments(user_adm=user_adm)
    deployments_v2 = deployments_v2_lib.DeploymentsV2(user_adm=user_adm)
    inventory = inventory_lib.Inventory(user_adm=user_adm)
    inventory_v2 = inventory_v2_lib.InventoryV2(user_adm=user_adm)


def authenticate(email, password, server_url):
    _init(email=email, password=password, server_url=server_url)


_init()
