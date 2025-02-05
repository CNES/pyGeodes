#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module regroups all decorators used in pygeodes"""
# -----------------------------------------------------------------------------
# Copyright (c) 2024, CNES
#
# REFERENCES:
# https://cnes.fr/
# -----------------------------------------------------------------------------

from functools import wraps

# stdlib imports -------------------------------------------------------
from typing import Callable

# local imports ---------------------------------------------------
from pygeodes.utils.exceptions import RequiresApiKeyException

# third-party imports -----------------------------------------------


def requires_api_key(
    _func: Callable = None, bypass_with_s3_credentials: bool = False
):
    """This decorator, on a Provider method, makes an api_key mandatory for this method, and raises an error if the provider config does not contain any api_key"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            for arg in args:
                if (
                    arg.__class__.__name__ == "Geodes"
                ):  # si l'argument est Geodes
                    if not arg.conf.has_api_key:
                        if bypass_with_s3_credentials:
                            if not arg.conf.has_s3_parameters():
                                raise RequiresApiKeyException(
                                    f"The use of function `{arg.__class__.__name__}.{func.__name__}` requires an api_key or s3 credentials, please specify some in your config JSON file"
                                )
                        else:

                            raise RequiresApiKeyException(
                                f"The use of function `{arg.__class__.__name__}.{func.__name__}` requires an api_key, please specify one in your config JSON file"
                            )

            return func(*args, **kwargs)

        return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)


def not_implemented(func: Callable):
    """This decorator, placed on a function, raises an error when the function is called, saying it's not implemented yet"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        raise NotImplementedError(
            f"the function {func.__name__} is not implemented yet"
        )

    return wrapper


def uses_session(func: Callable):
    """This decorator, placed on a method from :py:class:`pygeodes.utils.request.SyncRequestMaker`, opens an http session before executing the function and closes it after"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        for arg in args:
            if arg.__class__.__name__ == "SyncRequestMaker":
                arg.open_session()

                res = func(*args, **kwargs)

                arg.close_session()

                return res

    return wrapper
