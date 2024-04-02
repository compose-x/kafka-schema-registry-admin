#  SPDX-License-Identifier: Apache License 2.0
#  Copyright 2024 John Mille <john@ews-network.net>
import json
from copy import deepcopy

import pytest

from kafka_schema_registry_admin.client_wrapper.errors import (
    NotFoundException,
    UnexpectedException,
    UnprocessableEntity,
)


@pytest.fixture()
def schema_sample():
    return {
        "type": "record",
        "namespace": "com.mycorp.mynamespace",
        "name": "value_test_subject",
        "doc": "Sample schema to help you get started.",
        "fields": [
            {
                "name": "myField1",
                "type": "int",
                "doc": "The int type is a 32-bit signed integer.",
            },
            {
                "name": "myField2",
                "type": "double",
                "doc": "The double type is a double precision (64-bit) IEEE 754 floating-point number.",
            },
            {
                "name": "myField3",
                "type": "string",
                "doc": "The string is a unicode character sequence.",
            },
        ],
    }


def test_import_schema(local_registry, schema_sample):
    try:
        local_registry.get_subject_versions("test-subject4")
    except NotFoundException:
        print("Subject not found")
    found = local_registry.get_all_subjects(
        deleted=True, subject_prefix="test-subject4"
    ).json()
    print("FOUND ANY?", found)

    local_registry.put_subject_mode("test-subject4", "IMPORT", force=True)
    schema = local_registry.post_subject_schema_version(
        "test-subject4", schema_sample, version_id=1, schema_id=42, schema_type="AVRO"
    )
    print("Restored test-subject4", schema.json())
    assert schema.status_code in range(200, 300) and schema.json()["id"] == 42

    local_registry.delete_subject("test-subject4", permanent=True)


def test_import_schema_v2(local_registry, schema_sample):
    try:
        local_registry.get_subject_versions("test-subject4")
    except NotFoundException:
        print("Subject not found")
    found = local_registry.get_all_subjects(
        deleted=True, subject_prefix="test-subject4"
    ).json()
    print("FOUND ANY?", found)

    local_registry.put_mode("IMPORT", force=True)
    local_registry.put_subject_mode("test-subject4", "IMPORT")
    schema = local_registry.post_subject_schema_version(
        "test-subject4", schema_sample, version_id=1, schema_id=43, schema_type="AVRO"
    )
    print("Restored test-subject4", schema.json())
    assert schema.status_code in range(200, 300) and schema.json()["id"] == 43

    local_registry.delete_subject("test-subject4", permanent=True)


def test_fail_import_schema_v2(local_registry, schema_sample):
    try:
        local_registry.get_subject_versions("test-subject4")
    except NotFoundException:
        print("Subject not found")
    found = local_registry.get_all_subjects(
        deleted=True, subject_prefix="test-subject4"
    ).json()
    print("FOUND ANY?", found)

    local_registry.put_mode("READWRITE")
    local_registry.put_subject_mode("test-subject4", "READWRITE")
    with pytest.raises(UnprocessableEntity):
        local_registry.post_subject_schema_version(
            "test-subject4",
            schema_sample,
            version_id=1,
            schema_id=43,
            schema_type="AVRO",
        )
