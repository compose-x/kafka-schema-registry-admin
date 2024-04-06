#  SPDX-License-Identifier: Apache License 2.0
#  Copyright 2024 John Mille <john@ews-network.net>
import json
from copy import deepcopy

import pytest

from kafka_schema_registry_admin.client_wrapper.errors import (
    IncompatibleSchema,
    NotFoundException,
)


@pytest.mark.asyncio(scope="session")
async def test_reset_sr_mode(async_local_registry):
    await async_local_registry.put_mode("READWRITE")


@pytest.mark.asyncio(scope="session")
async def test_register_new_definition(async_local_registry, schema_sample):
    c = await async_local_registry.post_subject_schema_version(
        "test-subject4", schema_sample, normalize=True
    )
    r = await async_local_registry.get_schema_from_id(c.json()["id"])
    assert "test-subject4" in (await async_local_registry.get_all_subjects()).json()
    r = await async_local_registry.get_subject_versions("test-subject4")
    assert 1 in r.json()
    full_details = (
        await async_local_registry.get_subject_version_id("test-subject4", 1)
    ).json()
    schema = (
        await async_local_registry.get_subject_version_id_schema("test-subject4", 1)
    ).json()
    assert len(schema["fields"]) == len(json.loads(full_details["schema"])["fields"])


@pytest.mark.asyncio(scope="session")
async def test_subject_existing_schema_definition(async_local_registry, schema_sample):
    r = await async_local_registry.post_subject_schema(
        "test-subject4", schema_sample, "AVRO"
    )
    r = await async_local_registry.get_schema_versions_from_id(r.json()["id"])


@pytest.mark.asyncio(scope="session")
async def test_register_new_definition_updated(async_local_registry, schema_sample):
    new_version = deepcopy(schema_sample)
    new_version["fields"].append(
        {
            "doc": "The string is a unicode character sequence.",
            "name": "myField4",
            "type": "string",
        }
    )
    test = await async_local_registry.post_subject_schema(
        "test-subject4", schema_sample
    )
    latest = await async_local_registry.get_subject_versions_referencedby(
        "test-subject4", test.json()["version"]
    )

    new_compat = await async_local_registry.put_compatibility_subject_config(
        "test-subject4", "BACKWARD"
    )
    assert new_compat.json()["compatibility"] == "BACKWARD"
    compat = await async_local_registry.post_compatibility_subject_version_id(
        "test-subject4",
        test.json()["version"],
        new_version,
        verbose=True,
    )
    assert isinstance(compat.json()["is_compatible"], bool)
    is_compatible = compat.json()["is_compatible"]
    if is_compatible:
        r = await async_local_registry.post_subject_schema_version(
            "test-subject4", new_version, schema_type="AVRO"
        )

    await async_local_registry.put_compatibility_subject_config(
        "test-subject4", "FORWARD"
    )
    new_version["fields"].pop(0)


@pytest.mark.asyncio(scope="session")
async def test_get_all_subjects(async_local_registry):
    r = (await async_local_registry.get_all_subjects()).json()
    assert isinstance(r, list) and r
    r = await async_local_registry.get_all_subjects(subject_prefix="test-subject4")
    assert "test-subject4" in r.json()


@pytest.mark.asyncio(scope="session")
async def test_get_all_schema_types(async_local_registry):
    r = (await async_local_registry.get_schema_types()).json()
    assert isinstance(r, list) and r


@pytest.mark.asyncio(scope="session")
async def test_delete_subject(async_local_registry):
    versions = (await async_local_registry.get_subject_versions("test-subject4")).json()
    await async_local_registry.delete_subject(
        "test-subject4", permanent=False, version_id=versions[-1]
    )
    await async_local_registry.delete_subject("test-subject4", permanent=False)
    r = (await async_local_registry.get_all_subjects(deleted=True)).json()
    print(r)
    r = await async_local_registry.get_all_subjects(
        deleted=True, subject_prefix="test-subject4"
    )
    print("R2", r.json())
    await async_local_registry.delete_subject("test-subject4", permanent=True)
    r = (await async_local_registry.get_all_subjects(deleted=True)).json()
