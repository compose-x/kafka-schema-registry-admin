# SPDX-License-Identifier: Apache License 2.0
# Copyright 2024 John Mille <john@ews-network.net>

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from requests import Response

from urllib.parse import urlparse

import requests

from .errors import ApiGenericException, SchemaRegistryApiException, evaluate_api_return


class Client:
    """API Client wrapper around the requests"""

    def __init__(self, base_url: str, basic_auth: dict = None):
        self._base_url = base_url

        self._default_headers: dict = {
            "Accept": "application/json",
        }
        self._post_headers: dict = {
            "Accept": "application/json",
            "Content-Type": "application/vnd.schemaregistry.v1+json",
        }
        self.auth = None
        if basic_auth:
            self.auth = (
                basic_auth["basic_auth.username"],
                basic_auth["basic_auth.password"],
            )
        self.session = requests.Session()

    @evaluate_api_return
    def get(self, api_path: str, *args, **kwargs) -> Response:
        """Get the data from the api_path"""
        headers = kwargs.get("headers", {})
        if not headers:
            kwargs["headers"] = headers
        headers.update(self._default_headers)
        url: str = urlparse(self._base_url + api_path).geturl()

        response = self.session.get(url, auth=self.auth, *args, **kwargs)
        return response

    @evaluate_api_return
    def post(self, api_path: str, *args, **kwargs) -> Response:
        """POST the data from the api_path"""
        headers = kwargs.get("headers", {})
        if not headers:
            kwargs["headers"] = headers
        headers.update(self._default_headers)
        headers.update(self._post_headers)
        url: str = urlparse(self._base_url + api_path).geturl()
        response = self.session.post(url, auth=self.auth, *args, **kwargs)
        return response

    @evaluate_api_return
    def put(self, api_path: str, *args, **kwargs) -> Response:
        """PUT the data from the api_path"""
        headers = kwargs.get("headers", {})
        if not headers:
            kwargs["headers"] = headers
        headers.update(self._default_headers)
        url: str = urlparse(self._base_url + api_path).geturl()

        response = self.session.put(url, auth=self.auth, *args, **kwargs)
        return response

    @evaluate_api_return
    def delete(self, api_path: str, *args, **kwargs) -> Response:
        """DELETE the data from the api_path"""
        headers = kwargs.get("headers", {})
        if not headers:
            kwargs["headers"] = headers
        headers.update(self._default_headers)

        url: str = urlparse(self._base_url + api_path).geturl()
        response = self.session.delete(url, auth=self.auth, *args, **kwargs)
        return response
