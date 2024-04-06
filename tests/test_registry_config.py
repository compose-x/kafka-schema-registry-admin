#  SPDX-License-Identifier: Apache License 2.0
#  Copyright 2024 John Mille <john@ews-network.net>
import json
from copy import deepcopy
from os import path

import pytest

from kafka_schema_registry_admin import CompatibilityMode, RegistryMode, SchemaRegistry


def test_changing_compatibility(authed_local_registry):
    config = authed_local_registry.get_config().json()
    print("CONFIG 1?", config)
    authed_local_registry.put_config(
        compatibility=CompatibilityMode.FULL.value, normalize=True
    )
    config = authed_local_registry.get_config().json()
    print("CONFIG 2?", config)


def test_changing_mode(authed_local_registry):
    mode = authed_local_registry.get_mode(as_str=True)
    print("MODE?", mode)
    assert mode == RegistryMode.READWRITE.value

    authed_local_registry.put_mode(RegistryMode.READONLY.value)
    assert (
        authed_local_registry.get_mode().json()["mode"] == RegistryMode.READONLY.value
    )

    authed_local_registry.put_mode(RegistryMode.IMPORT.value)
    assert authed_local_registry.get_mode().json()["mode"] == RegistryMode.IMPORT.value
