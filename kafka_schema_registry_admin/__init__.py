# SPDX-License-Identifier: Apache License 2.0
# Copyright 2021 John Mille <john@ews-network.net>

"""Top-level package for Kafka schema registry admin."""

__author__ = """JohnPreston"""
__email__ = "john@ews-network.net"
__version__ = "0.3.0"

from .kafka_schema_registry_admin import SchemaRegistry

__all__ = ["SchemaRegistry"]
