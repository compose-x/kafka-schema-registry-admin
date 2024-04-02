#  SPDX-License-Identifier: Apache License 2.0
#  Copyright 2024 John Mille <john@ews-network.net>

import json
from copy import deepcopy
from os import path

import pytest

from kafka_schema_registry_admin.async_schema_registry import (
    CompatibilityMode,
    RegistryMode,
)


@pytest.mark.asyncio(scope="session")
async def test_changing_compatibility(async_local_registry):
    config = (await async_local_registry.get_config()).json()
    print("CONFIG 1?", config)
    await async_local_registry.put_config(
        compatibility=CompatibilityMode.FULL.value, normalize=True
    )
    config = (await async_local_registry.get_config()).json()
    print("CONFIG 2?", config)


@pytest.mark.asyncio(scope="session")
async def test_changing_mode(async_local_registry, async_client):
    mode = await async_local_registry.get_mode(async_client=async_client, as_str=True)
    assert mode == RegistryMode.READWRITE.value

    await async_local_registry.put_mode(RegistryMode.READONLY.value)
    assert (await async_local_registry.get_mode()).json()[
        "mode"
    ] == RegistryMode.READONLY.value

    await async_local_registry.put_mode(RegistryMode.IMPORT.value)
    assert (await async_local_registry.get_mode()).json()[
        "mode"
    ] == RegistryMode.IMPORT.value

    await async_local_registry.put_mode(RegistryMode.READWRITE.value)
