# SPDX-License-Identifier: Apache License 2.0
# Copyright 2024 John Mille <john@ews-network.net>

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import Response as Response

from urllib.parse import urlparse

import httpx


class Client:
    """API Client wrapper around the httpx library"""

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

    async def get(
        self, api_path: str, async_client: httpx.AsyncClient = None, *args, **kwargs
    ) -> Response:
        """Get the data from the api_path"""
        headers = kwargs.get("headers", {})
        if not headers:
            kwargs["headers"] = headers
        headers.update(self._default_headers)
        url: str = urlparse(self._base_url + api_path).geturl()
        if not async_client:
            async with httpx.AsyncClient() as async_client:
                response = await async_client.get(url, auth=self.auth, *args, **kwargs)
        else:
            response = await async_client.get(url, auth=self.auth, *args, **kwargs)
        return response

    async def post(
        self, api_path: str, async_client: httpx.AsyncClient = None, *args, **kwargs
    ) -> Response:
        """POST the data from the api_path"""
        headers = kwargs.get("headers", {})
        if not headers:
            kwargs["headers"] = headers
        headers.update(self._default_headers)
        headers.update(self._post_headers)
        url: str = urlparse(self._base_url + api_path).geturl()
        if not async_client:
            async with httpx.AsyncClient() as async_client:
                response = await async_client.post(url, auth=self.auth, *args, **kwargs)
        else:
            response = await async_client.post(url, auth=self.auth, *args, **kwargs)
        return response

    async def put(
        self, api_path: str, async_client: httpx.AsyncClient = None, *args, **kwargs
    ) -> Response:
        """PUT the data from the api_path"""
        headers = kwargs.get("headers", {})
        if not headers:
            kwargs["headers"] = headers
        headers.update(self._default_headers)
        url: str = urlparse(self._base_url + api_path).geturl()
        if not async_client:
            async with httpx.AsyncClient() as async_client:
                response = await async_client.put(url, auth=self.auth, *args, **kwargs)
        else:
            response = await async_client.put(url, auth=self.auth, *args, **kwargs)
        return response

    async def delete(
        self, api_path: str, async_client: httpx.AsyncClient = None, *args, **kwargs
    ) -> Response:
        """DELETE the data from the api_path"""
        headers = kwargs.get("headers", {})
        if not headers:
            kwargs["headers"] = headers
        headers.update(self._default_headers)

        url: str = urlparse(self._base_url + api_path).geturl()
        if not async_client:
            async with httpx.AsyncClient() as async_client:
                response = await async_client.delete(
                    url, auth=self.auth, *args, **kwargs
                )
        else:
            response = await async_client.delete(url, auth=self.auth, *args, **kwargs)
        return response
