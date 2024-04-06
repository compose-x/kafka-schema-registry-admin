"""Pytest configuration and hooks"""

from os import path

import httpx
import pytest
from testcontainers.compose import DockerCompose

from kafka_schema_registry_admin import SchemaRegistry
from kafka_schema_registry_admin.async_schema_registry import SchemaRegistry as AsyncSR

HERE = path.abspath(path.dirname(__file__))


docker_compose = DockerCompose(
    path.abspath(f"{HERE}/.."),
    compose_file_name="docker-compose.yaml",
    wait=True,
    pull=True,
)

docker_compose.stop(down=True)
docker_compose.start()
sr_port = int(docker_compose.get_service_port("schema-registry", 8081))
base_url: str = f"http://localhost:{sr_port}"
docker_compose.wait_for(f"{base_url}/subjects")


@pytest.fixture(scope="session")
def async_client():
    return httpx.AsyncClient()


@pytest.fixture(scope="session")
def local_registry():
    return SchemaRegistry(base_url)


@pytest.fixture(scope="session")
def authed_local_registry():
    return SchemaRegistry(
        base_url,
        **{"basic_auth.username": "confluent", "basic_auth.password": "confluent"},
    )


@pytest.fixture(scope="session")
def async_local_registry(async_client):
    return AsyncSR(
        base_url,
        **{"basic_auth.username": "confluent", "basic_auth.password": "confluent"},
    )


def pytest_sessionfinish(session, exitstatus):
    docker_compose.stop()
    print("Testing session has finished")
    print(f"Exit status: {exitstatus}")


@pytest.fixture(scope="session")
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
