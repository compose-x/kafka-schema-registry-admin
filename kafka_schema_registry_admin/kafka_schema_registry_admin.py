# SPDX-License-Identifier: Apache License 2.0
# Copyright 2024 John Mille <john@ews-network.net>

"""
Main module for schema_registry_admin
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import CompatibilityMode, RegistryMode, Type

if TYPE_CHECKING:
    from requests import Response

import json
from logging import getLogger
from urllib.parse import urlencode

from .client_wrapper import Client
from .client_wrapper.errors import NotFoundException

LOG = getLogger()
LOG.setLevel("WARN")


class SchemaRegistry:

    def __init__(self, base_url: str, *args, **kwargs):
        username = kwargs.get("basic_auth.username", None)
        password = kwargs.get("basic_auth.password", None)
        basic_auth: dict = {}
        if username and password:
            basic_auth: dict = {
                "basic_auth.username": username,
                "basic_auth.password": password,
            }
        self.client: Client = Client(str(base_url), basic_auth)

    @property
    def subjects(self) -> list[str]:
        """
        Property to get the list of subjects in the schema registry
        """
        return self.get_all_subjects().json()

    def get_all_subjects(
        self, subject_prefix: str = None, deleted: bool = False
    ) -> Response:
        """
        Method to get the list of subjects in the schema registry
        https://docs.confluent.io/platform/current/schema-registry/develop/api.html#get--subjects

        :raises: requests.exceptions.HTTPError
        """
        url_path: str = "/subjects"
        if subject_prefix and deleted:
            url_path += "?" + urlencode(
                {"subjectPrefix": subject_prefix, "deleted": "true"}
            )
        elif subject_prefix:
            url_path += f"?subjectPrefix={subject_prefix}"
        elif deleted:
            url_path += f"?deleted=true"
        return self.client.get(url_path)

    def get_subject_versions(self, subject_name: str) -> Response:
        """
        Method to get the list of subjects in the schema registry
        https://docs.confluent.io/platform/current/schema-registry/develop/api.html#get--subjects-(string-%20subject)-versions
        """
        return self.client.get(f"/subjects/{subject_name}/versions")

    def get_subject_version_id(
        self, subject_name: str, version_id: str | int = "latest"
    ) -> Response:
        """
        Method to get the list of subjects in the schema registry
        `API doc <https://docs.confluent.io/platform/current/schema-registry/develop/api.html#get--subjects-(string-%20subject)-versions-(versionId-%20version)>`__
        """
        url_path: str = f"/subjects/{subject_name}/versions/{version_id}"
        LOG.debug(url_path)
        return self.client.get(url_path)

    def get_subject_version_id_schema(
        self, subject_name: str, version_id: str | int = "latest"
    ) -> Response:
        """
        Method to get the list of subjects in the schema registry
        `API Doc <https://docs.confluent.io/platform/current/schema-registry/develop/api.html#get--subjects-(string-%20subject)-versions-(versionId-%20version)-schema>`__
        """
        url_path: str = f"/subjects/{subject_name}/versions/{version_id}/schema"
        LOG.debug(url_path)
        return self.client.get(url_path)

    def get_subject_versions_referencedby(self, subject_name, version_id) -> Response:
        """
        `API Doc <https://docs.confluent.io/platform/current/schema-registry/develop/api.html#get--subjects-(string-%20subject)-versions-versionId-%20version-referencedby>`__
        """
        req = self.client.get(
            f"/subjects/{subject_name}/versions/{version_id}/referencedby"
        )
        return req

    def post_subject_schema(
        self, subject_name, definition, schema_type=None
    ) -> Response:
        """
        Checks if the schema definition has already been registered with the subject.
        Succeeds only if both the schema and the subject are registered. Returns 404 otherwise.
        40401 - Subject not found
        40403 - Schema not found
        `API Doc <https://docs.confluent.io/platform/current/schema-registry/develop/api.html#post--subjects-(string-%20subject)>`__
        """
        if isinstance(definition, dict):
            definition = str(json.dumps(definition))
        if schema_type is None:
            schema_type = Type["AVRO"].value
        else:
            schema_type = Type[schema_type].value

        payload = {"schema": definition, "schemaType": schema_type}
        url = f"/subjects/{subject_name}"
        req = self.client.post(url, json=payload)

        return req

    def post_subject_schema_version(
        self,
        subject_name,
        definition,
        normalize: bool = False,
        schema_type=None,
        version_id: int = None,
        schema_id: int = None,
    ) -> Response:
        """
        `API Doc <https://docs.confluent.io/platform/current/schema-registry/develop/api.html#post--subjects-(string-%20subject)-versions>`__
        Creates a new schema version for the given subject (and registers the subject if did not exist).
        Returns the schema ID.
        """
        try:
            return self.post_subject_schema(subject_name, definition, schema_type)
        except NotFoundException:
            if isinstance(definition, dict):
                definition = str(json.dumps(definition))
            if schema_type is None:
                schema_type = Type["AVRO"].value
            else:
                schema_type = Type[schema_type].value

            payload = {"schema": definition, "schemaType": schema_type}
            url = f"/subjects/{subject_name}/versions"
            if normalize:
                url = f"{url}?normalize=true"
            """When trying to do recovery, SR must be in import mode either globally or for the subject itself."""
            if version_id and schema_id:
                payload["version"] = version_id
                payload["id"] = schema_id

            req = self.client.post(url, json=payload)
            return req

    def delete_subject(
        self, subject_name, version_id=None, permanent=False
    ) -> Response:
        """
        Method to delete a subject entirely or a specific version
        https://docs.confluent.io/platform/current/schema-registry/develop/api.html#delete--subjects-(string-%20subject)
        https://docs.confluent.io/platform/current/schema-registry/develop/api.html#post--subjects-(string-%20subject)-versions

        :param str subject_name:
        :param int version_id:
        :param bool permanent:
        """
        url = f"/subjects/{subject_name}"
        if version_id:
            url = f"{url}/versions/{version_id}"
        try:
            return self.client.delete(url)
        except NotFoundException:
            subjects = self.get_all_subjects(
                subject_prefix=subject_name, deleted=True
            ).json()
            if subject_name in subjects and permanent:
                return self.client.delete(f"{url}?permanent=true")
        if permanent:
            permanent_url = f"{url}?permanent=true"
            return self.client.delete(permanent_url)

    def get_schema_types(self) -> Response:
        """
        Method to get the list of schema types and return the request object
        """
        url = f"/schemas/types"
        req = self.client.get(url)
        return req

    def get_schema_from_id(self, schema_id) -> Response:
        url = f"/schemas/ids/{schema_id}"
        LOG.debug(url)
        req = self.client.get(url)
        return req

    def get_schema_versions_from_id(self, schema_id):
        """
        Retrieve the versions for a given schema by its ID
        """
        url = f"/schemas/ids/{schema_id}/versions"
        req = self.client.get(url)
        return req

    def post_compatibility_subject_versions(
        self,
        subject_name,
        definition,
        verbose: bool = False,
        schema_type: str | Type = None,
        references: list = None,
    ) -> Response:
        url = f"/compatibility/subjects/{subject_name}/versions"
        payload = self.set_subject_validity_payload(
            url, definition, schema_type, verbose=verbose, references=references
        )
        return self.client.post(url, json=payload)

    def post_compatibility_subject_version_id(
        self,
        subject_name,
        version_id,
        definition,
        verbose: bool = False,
        schema_type: str | Type = None,
        references: list = None,
    ) -> Response:
        url = f"/compatibility/subjects/{subject_name}/versions/{version_id}"
        payload = self.set_subject_validity_payload(
            url, definition, schema_type, verbose=verbose, references=references
        )
        return self.client.post(url, json=payload)

    @staticmethod
    def set_subject_validity_payload(
        url: str,
        definition,
        schema_type,
        verbose: bool = False,
        references: list = None,
    ) -> dict:
        if verbose:
            url = f"{url}?verbose=true"
        LOG.debug(url)
        if isinstance(definition, dict):
            definition = str(json.dumps(definition))
        if schema_type is None:
            schema_type = Type["AVRO"].value
        else:
            schema_type = Type[schema_type].value

        payload = {"schema": definition, "schemaType": schema_type}
        if references and isinstance(references, list):
            payload["references"] = references
        return payload

    def get_compatibility_subject_config(self, subject_name) -> Response:
        url = f"/config/{subject_name}/"
        req = self.client.get(url)
        return req

    def put_compatibility_subject_config(self, subject_name, compatibility) -> Response:
        url = f"/config/{subject_name}/"
        payload = {"compatibility": compatibility}
        req = self.client.put(url, json=payload)
        return req

    def get_mode(self, as_str: bool = False) -> Response | str:
        """
        `API Doc <https://docs.confluent.io/platform/current/schema-registry/develop/api.html#mode>`__
        """
        url_path: str = "/mode"
        req = self.client.get(url_path)
        if as_str:
            return RegistryMode[req.json().get("mode")].value
        return req

    def put_mode(self, mode: str | RegistryMode, force: bool = False) -> Response:
        """
        `API Doc <https://docs.confluent.io/platform/current/schema-registry/develop/api.html#put--mode>`__
        """
        url_path: str = "/mode"
        if force:
            url_path += "?force=true"
        req = self.client.put(url_path, json={"mode": mode})
        return req

    def get_subject_mode(self, subject_name: str) -> Response:
        """
        `API Doc <https://docs.confluent.io/platform/current/schema-registry/develop/api.html#get--mode-(string-%20subject)>`__
        """
        url_path: str = f"/mode/{subject_name}"
        req = self.client.get(url_path)
        return req

    def put_subject_mode(
        self, subject_name: str, mode: str | RegistryMode, force: bool = False
    ) -> Response:
        """
        `API Doc <https://docs.confluent.io/platform/current/schema-registry/develop/api.html#put--mode-(string-%20subject)>`__
        """
        url_path: str = f"/mode/{subject_name}"
        if force:
            url_path += "?force=true"
        req = self.client.put(url_path, json={"mode": mode})
        return req

    def get_config(self):
        """
        `API Doc <https://docs.confluent.io/platform/current/schema-registry/develop/api.html#get--config>`__
        """
        url_path: str = "/config"
        req = self.client.get(url_path)
        return req

    def put_config(
        self,
        alias: str = None,
        normalize: bool = False,
        compatibility: str | CompatibilityMode = "NONE",
    ):
        """
        `API Doc <https://docs.confluent.io/platform/current/schema-registry/develop/api.html#put--config>`__
        """
        url_path: str = "/config"
        payload: dict = {}
        if compatibility:
            payload["compatibility"] = compatibility
        if alias:
            payload["alias"] = alias
        if normalize:
            payload["normalize"] = normalize
        req = self.client.put(url_path, json=payload)
        return req

    def get_subject_config(
        self,
        subject: str,
        default: bool = False,
        alias: str = None,
        normalize: bool = False,
        compatibility: str | CompatibilityMode = "NONE",
    ):
        """
        `API Doc <https://docs.confluent.io/platform/current/schema-registry/develop/api.html#get--config>`__
        """
        url_path: str = f"/config/{subject}"
        if default:
            url_path += "?defaultToGlobal=true"
        payload: dict = {}
        if compatibility:
            payload["compatibility"] = compatibility
        if alias:
            payload["alias"] = alias
        if normalize:
            payload["normalize"] = normalize
        req = self.client.get(url_path, json=payload)
        return req

    def put_subject_config(
        self,
        subject: str,
        alias: str = None,
        normalize: bool = False,
        compatibility: str | CompatibilityMode = "NONE",
    ):
        """
        `API Doc <https://docs.confluent.io/platform/current/schema-registry/develop/api.html#put--config>`__
        """
        url_path: str = f"/config/{subject}"
        payload: dict = {}
        if compatibility:
            payload["compatibility"] = compatibility
        if alias:
            payload["alias"] = alias
        if normalize:
            payload["normalize"] = normalize
        req = self.client.put(url_path, json=payload)
        return req

    def delete_subject_config(
        self,
        subject: str,
        alias: str = None,
        normalize: bool = False,
        compatibility: str | CompatibilityMode = "NONE",
    ):
        """
        `API Doc <https://docs.confluent.io/platform/current/schema-registry/develop/api.html#delete--config-(string-%20subject)>`__
        """
        url_path: str = f"/config/{subject}"
        req = self.client.delete(url_path)
        return req
