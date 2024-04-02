# SPDX-License-Identifier: Apache License 2.0
# Copyright 2024 John Mille <john@ews-network.net>

from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any

from requests import exceptions as req_exceptions


def keyisset(_key: Any, _dict: dict):
    return isinstance(_dict, dict) and _dict.get(_key, False)


class ApiGenericException(Exception):
    """
    Generic class handling Exceptions
    """

    def __init__(self, msg, code, details):
        """

        :param msg:
        :param code:
        :param details:
        """
        super().__init__(msg, code, details)
        self.code = code
        self.details = details


class ConflictException(ApiGenericException):
    """
    Exception class for 409 Conflict
    """

    def __init__(self, code, details):
        if isinstance(details[0], str):
            super().__init__(details[0], code, details[1:])
        else:
            if isinstance(details[-1], dict) and keyisset("message", details[-1]):
                error_message = details[-1]["message"]
                if error_message.startswith(
                    "Schema being registered is incompatible with an earlier schema for subject"
                ):
                    raise IncompatibleSchema(code, details[1:])
            else:
                super().__init__(details, code, details[1:])


class IncompatibleSchema(ApiGenericException):
    """
    Exception class for 409
    """

    def __init__(self, code, details):
        super().__init__("Incompatible Schema", code, details)


class NotFoundException(ApiGenericException):
    """
    Exception class for 404 Not Found
    """

    def __init__(self, code, details):
        super().__init__("Not Found", code, details)


class UnauthorizedException(ApiGenericException):
    """
    Exception class for 401 Unauthorized
    """

    def __init__(self, code, details):
        super().__init__("Unauthorized", code, details)


class ForbiddenException(ApiGenericException):
    """
    Exception class for 403 Forbidden
    """

    def __init__(self, code, details):
        super().__init__("Forbidden", code, details)


class UnprocessableEntity(ApiGenericException):
    def __init__(self, code, details):
        super().__init__("Unprocessable Entity", code, details)


class UnexpectedException(ApiGenericException):
    def __init__(self, code, details):
        super().__init__("Unexpected Error", code, details)


class SchemaRegistryApiException(ApiGenericException):
    """
    Top class for DatabaseUser exceptions
    """

    EXCEPTION_CLASSES = {
        409: ConflictException,
        404: NotFoundException,
        401: UnauthorizedException,
        403: ForbiddenException,
        422: UnprocessableEntity,
    }

    def __init__(self, code, details):
        exception_class = self.EXCEPTION_CLASSES.get(code, UnexpectedException)
        super().__init__(
            details[0] is isinstance(details[0], str)
            and details[0]
            or "SchemaRegistry Api Error",
            code,
            details,
        )
        self.exception_instance = exception_class(code, details)


def evaluate_api_return(function):
    @functools.wraps(function)
    def wrapped_answer(*args, **kwargs):
        try:
            payload = function(*args, **kwargs)
            if payload.status_code not in [200, 201, 202, 204] and not keyisset(
                "ignore_failure", kwargs
            ):
                try:
                    details = (args[0:2], payload.json())
                except req_exceptions.JSONDecodeError:
                    details = (args[0:2], payload.text)
                schema_exception = SchemaRegistryApiException(
                    payload.status_code, details
                )
                raise schema_exception.exception_instance

            elif keyisset("ignore_failure", kwargs):
                return payload
            return payload
        except req_exceptions.RequestException as error:
            print(error)
            raise

    return wrapped_answer
