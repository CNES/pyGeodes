#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains all things related to date and time"""
# -----------------------------------------------------------------------------
# Copyright (c) 2024, CNES
#
# REFERENCES:
# https://cnes.fr/
# -----------------------------------------------------------------------------

# stdlib imports -------------------------------------------------------
from datetime import datetime, timedelta
from typing import Tuple

# local imports ---------------------------------------------------
from pygeodes.utils.consts import (
    DATETIME_FORMAT,
    OTHER_SUPPORTED_DATETIME_FORMATS,
)

# third-party imports -----------------------------------------------


def time_ago(date: datetime) -> str:
    """Returns a string with how long ago was the date provided

    Parameters
    ----------
    date : datetime
        a date

    Returns
    -------
    str
        a string with how long ago the date was
    """
    delta = datetime.now() - date
    if delta.seconds > 3600:
        return f"{delta.seconds // 3600} hours ago"
    elif delta.seconds > 60:
        return f"{delta.seconds // 60} minutes ago"
    else:
        return f"{delta.seconds} seconds ago"


def is_in_format(string: str, format: str) -> bool:
    """Returns wether string ``string`` is in format ``format``

    Parameters
    ----------
    string : str
        a datetime string
    format : str
        a datetime format string

    Returns
    -------
    bool
        wether string ``string`` is in format ``format``
    """
    try:
        datetime.strptime(string, format)
        return True
    except:
        return False


def complete_datetime_from_str(string: str) -> str:
    """Returns a valid string for format pygeodes.utils.consts.DATETIME_FORMAT from a non-valid string (under some defined formats)

    Parameters
    ----------
    string : str
        a non valid datetime string

    Returns
    -------
    str
        a valid datetime string

    Examples
    --------

    .. code-block:: python

        complete_datetime_from_str("2023-09-23") # this returns "2023-09-23T00:00:00.0Z"

    Raises
    ------
    Exception
    """

    for fmt in OTHER_SUPPORTED_DATETIME_FORMATS:
        if is_in_format(string, fmt):
            obj = datetime.strptime(string, fmt)
            return datetime_to_str(obj)

    raise Exception(
        f"Unkown datetime format for date {string} (supported formats : {OTHER_SUPPORTED_DATETIME_FORMATS})"
    )


def str_to_datetime(string: str) -> datetime:
    """Returns a ``datetime`` object from the provided datetime string

    Parameters
    ----------
    string : str
        a datetime string

    Returns
    -------
    datetime
        a datetime object from the string

    See Also
    --------
    datetime_to_str : to do the exact inverse
    """
    return datetime.strptime(string, DATETIME_FORMAT)


def datetime_to_str(datetime_obj: datetime) -> str:
    """Returns a datetime string from a datetime obj

    Parameters
    ----------
    datetime_obj : datetime
        a datetime object

    Returns
    -------
    str
        a datetime string from the object

    See Also
    --------
    str_to_datetime : to do the exact inverse

    """
    return datetime_obj.strftime(DATETIME_FORMAT)


def a_day_ago() -> datetime:
    """Returns a datetime object from 24h ago

    Returns
    -------
    datetime
        a datetime object from 24h ago
    """
    return datetime.now() - timedelta(days=1)


def a_week_ago() -> datetime:
    """Returns a datetime object from a week ago

    Returns
    -------
    datetime
        a datetime object from a week ago
    """
    return datetime.now() - timedelta(days=7)


def today() -> Tuple[datetime, datetime]:
    """Returns two datetime objects, today at first time (00:00), today at last time (23:59)

    Returns
    -------
    Tuple[datetime,datetime]
        today at first time (00:00), today at last time (23:59)
    """
    return datetime.combine(
        datetime.today(), datetime.min.time()
    ), datetime.combine(datetime.today(), datetime.max.time())
