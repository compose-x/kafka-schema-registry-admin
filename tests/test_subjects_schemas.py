#  SPDX-License-Identifier: Apache License 2.0
#  Copyright 2024 John Mille <john@ews-network.net>
import json
from copy import deepcopy

import pytest

from kafka_schema_registry_admin.client_wrapper.errors import (
    IncompatibleSchema,
    NotFoundException,
)


def test_reset_sr_mode(local_registry):
    local_registry.put_mode("READWRITE")


def test_register_new_definition(authed_local_registry, schema_sample):
    c = authed_local_registry.post_subject_schema_version(
        "test-subject4", schema_sample, normalize=True
    )
    r = authed_local_registry.get_schema_from_id(c.json()["id"])
    assert "test-subject4" in authed_local_registry.subjects
    r = authed_local_registry.get_subject_versions("test-subject4")
    assert 1 in r.json()
    full_details = authed_local_registry.get_subject_version_id(
        "test-subject4", 1
    ).json()
    schema = authed_local_registry.get_subject_version_id_schema(
        "test-subject4", 1
    ).json()
    assert len(schema["fields"]) == len(json.loads(full_details["schema"])["fields"])


def test_subject_existing_schema_definition(local_registry, schema_sample):
    r = local_registry.post_subject_schema("test-subject4", schema_sample, "AVRO")
    r = local_registry.get_schema_versions_from_id(r.json()["id"])


def test_register_new_definition_updated(local_registry, schema_sample):
    new_version = deepcopy(schema_sample)
    test = local_registry.post_subject_schema("test-subject4", schema_sample)
    latest = local_registry.get_subject_versions_referencedby(
        "test-subject4", test.json()["version"]
    )
    new_version["fields"].append(
        {
            "doc": "The string is a unicode character sequence.",
            "name": "myField4",
            "type": "string",
        }
    )
    with pytest.raises(NotFoundException):
        local_registry.get_compatibility_subject_config("test-subject4")
    local_registry.put_compatibility_subject_config("test-subject4", "BACKWARD")
    compat = local_registry.post_compatibility_subject_version_id(
        "test-subject4",
        test.json()["version"],
        new_version,
        verbose=True,
    )
    assert isinstance(compat.json()["is_compatible"], bool)
    is_compatible = compat.json()["is_compatible"]
    if is_compatible:
        r = local_registry.post_subject_schema_version(
            "test-subject4", new_version, schema_type="AVRO"
        )
    with pytest.raises(IncompatibleSchema):
        new_version["fields"].append({"type": "string", "name": "surname"})
        r = local_registry.post_subject_schema_version(
            "test-subject4", new_version, schema_type="AVRO"
        )
    local_registry.put_compatibility_subject_config("test-subject4", "FORWARD")
    new_version["fields"].pop(0)
    with pytest.raises(IncompatibleSchema):
        r = local_registry.post_subject_schema_version(
            "test-subject4", new_version, schema_type="AVRO"
        )


def test_get_all_subjects(local_registry):
    r = local_registry.get_all_subjects().json()
    assert isinstance(r, list) and r
    r = local_registry.get_all_subjects(subject_prefix="test-subject4")
    assert "test-subject4" in r.json()


def test_get_all_schema_types(local_registry):
    r = local_registry.get_schema_types().json()
    assert isinstance(r, list) and r


def test_delete_subject(local_registry):
    versions = local_registry.get_subject_versions("test-subject4").json()
    local_registry.delete_subject(
        "test-subject4", permanent=False, version_id=versions[-1]
    )
    local_registry.delete_subject("test-subject4", permanent=False)
    r = local_registry.get_all_subjects(deleted=True).json()
    print(r)
    r = local_registry.get_all_subjects(deleted=True, subject_prefix="test-subject4")
    print("R2", r.json())
    local_registry.delete_subject("test-subject4", permanent=True)
    r = local_registry.get_all_subjects(deleted=True).json()


def test_error_delete_subject(local_registry):
    with pytest.raises(NotFoundException):
        local_registry.delete_subject("test-subject4", permanent=True)
