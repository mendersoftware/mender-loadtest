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
import requests


logger = logging.getLogger()


def do_get_call(url, status_code=200, **kwargs):
    _r = requests.get(url, verify=False, **kwargs)
    if _r.status_code != status_code:
        logger.warning(
            "Call: GET %s. Status code: %s. Content of the response: %s"
            % (url, _r.status_code, _r.text)
        )
        return None
    try:
        _content = _r.json()
    except ValueError:
        return {}
    return _content


def do_post_call(url, status_code=200, text=False, **kwargs):
    _r = requests.post(url, verify=False, **kwargs)
    if _r.status_code != status_code:
        logger.warning(
            "Call: POST %s. Status code: %s. Content of the response: %s"
            % (url, _r.status_code, _r.text)
        )
        return None
    if text:
        return _r.text
    else:
        try:
            _content = _r.json()
        except ValueError:
            return {}
        return _content


def do_put_call(url, status_code=200, **kwargs):
    _r = requests.put(url, verify=False, **kwargs)
    if _r.status_code != status_code:
        logger.warning(
            "Call: PUT %s. Status code: %s. Content of the response: %s"
            % (url, _r.status_code, _r.text)
        )
        return None
    try:
        _content = _r.json()
    except ValueError:
        return {}
    return _content


def do_delete_call(url, status_code=200, **kwargs):
    _r = requests.delete(url, verify=False, **kwargs)
    if _r.status_code != status_code:
        logger.warning(
            "Call: DELETE %s. Status code: %s. Content of the response: %s"
            % (url, _r.status_code, _r.text)
        )
        return None
    try:
        _content = _r.json()
    except ValueError:
        return {}
    return _content
