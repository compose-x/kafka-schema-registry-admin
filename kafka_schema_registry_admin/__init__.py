# SPDX-License-Identifier: Apache License 2.0
# Copyright 2024 John Mille <john@ews-network.net>

"""Top-level package for Kafka schema registry admin."""

from __future__ import annotations

__author__ = """JohnPreston"""
__email__ = "john@ews-network.net"
__version__ = "0.4.1"

from enum import Enum


class RegistryMode(Enum):
    IMPORT = "IMPORT"
    READONLY = "READONLY"
    READWRITE = "READWRITE"


class CompatibilityMode(Enum):
    BACKWARD = "BACKWARD"
    BACKWARD_TRANSITIVE = "BACKWARD_TRANSITIVE"
    FORWARD = "FORWARD"
    FORWARD_TRANSITIVE = "FORWARD_TRANSITIVE"
    FULL = "FULL"
    FULL_TRANSITIVE = "FULL_TRANSITIVE"
    NONE = "NONE"


class Type(Enum):
    AVRO = "AVRO"
    JSON = "JSON"
    PROTOBUFF = "PROTOBUF"


from .kafka_schema_registry_admin import SchemaRegistry

__all__ = ["SchemaRegistry"]
