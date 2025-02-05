#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module regroups all functions related to file INPUT/OUTPUT"""
# -----------------------------------------------------------------------------
# Copyright (c) 2024, CNES
#
# REFERENCES:
# https://cnes.fr/
# -----------------------------------------------------------------------------

import hashlib

# stdlib imports -------------------------------------------------------
import json
import os
import re
from difflib import SequenceMatcher as SM
from json import JSONEncoder
from pathlib import Path
from time import perf_counter
from typing import List

from pygeodes.utils.consts import (
    FOLDER_CONSIDERED_BIG_SIZE,
    MAX_TIME_BEFORE_ABORTING_FOLDER_CHECKSUM,
)

# local imports ---------------------------------------------------
from pygeodes.utils.logger import logger

# third-party imports -----------------------------------------------


DEFAULT_FILESEARCH_TIMEOUT = 2


# this piece of code is used to make stac items json serializable
def wrapped_default(self, obj):
    return getattr(obj.__class__, "__json__", wrapped_default.default)(obj)


wrapped_default.default = JSONEncoder().default

JSONEncoder.original_default = JSONEncoder.default
JSONEncoder.default = wrapped_default


def file_exists(filepath: str, raise_exception: bool = True) -> bool:
    """This checks if the file exists, and, in function of a boolean parameter, raises an exception if it doesn't

    Parameters
    ----------
    filepath : str
        the filepath to check the existence of
    raise_exception : bool, optional
        whether to raise an exception, by default True

    Returns
    -------
    bool
        whether the file exists

    Raises
    ------
    FileNotFoundError
        error raised if the file doesn't exist

    See Also
    --------
    similar_filenames : to find the most similar filenames to a filename

    Examples
    --------

    .. code-block:: python

        name = "file.txt"
        exists = file_exists(name)

    """
    filepath = os.path.abspath(filepath)
    exists = os.path.exists(filepath)
    if exists:
        return True
    else:
        if raise_exception:
            raise FileNotFoundError(f"The file {filepath} doesn't exist")
        else:
            return False


def similar_filenames(
    filename: str, other_filenames: List[str], nb: int = 10
) -> List[str]:
    """This function returns the ``nb`` most resembling filenames to the filename provided in the list of filenames

    Args:
        `filename` (``str``): the filename
        `other_filenames` (``List[str]``): the other filenames to be compared to
        `nb` (``int``, optional): the number of filenames to keep. Defaults to 10.

    Returns:
        ``List[str]``: the most resembling filenames
    """
    similarities = sorted(
        [
            (SM(None, filename, other_filename).ratio(), other_filename)
            for other_filename in other_filenames
        ],
        key=lambda tp: tp[0],
        reverse=True,
    )
    return [tp[1] for tp in similarities][
        :nb
    ]  # on ne retourne que les nb premiers noms de fichiers


def find_unused_filename(filepath: str) -> str:
    """This functions finds an unused filename for the filepath provided by adding -{number} after

    Parameters
    ----------
    filepath : str
        the original filename

    Returns
    -------
    str
        an unused filename
    """
    if file_exists(filepath, raise_exception=False):
        root, ext = os.path.splitext(filepath)
        i = 1
        filepath = f"{root}-{i}{ext}"
        while file_exists(filepath, raise_exception=False):
            i += 1
            filepath = f"{root}-{i}{ext}"
        return filepath

    else:
        return filepath


def write_json(content: dict, filepath: str) -> None:
    """This functions dumps a dict at a filepath

    Parameters
    ----------
    content : dict
        the dict to dump
    filepath : str
        the filepath to dump to

    See also
    --------
    load_json : to read a JSON from a file
    """
    with open(filepath, "w") as file:
        json.dump(content, file, indent=4)


def load_json(filepath: str) -> dict:
    """This functions loads a JSON into a Python dict from a filepath

    Parameters
    ----------
    filepath : str
        the file to load the dict from

    Returns
    -------
    dict
        the dict loaded

    Raises
    ------
    Exception
        an Exception if the JSON is not a valid JSON

    See also
    --------
    write_json : to dump a Python dict into a JSON file
    """
    try:
        with open(filepath, "r") as file:
            content = json.load(file)
        return content
    except json.decoder.JSONDecodeError:
        raise Exception(f"The JSON file {filepath} is not a valid JSON")


def get_homedir() -> Path:
    """To get the home directory path of the current user

    Returns
    -------
    Path
        the homedir
    """
    # maybe only works on unix systems ?
    return Path(os.path.expanduser("~"))


def compute_md5(filepath: str) -> str:
    """Computes md5sum of the contents of the given filepath"""

    logger.debug(f"checking md5 for {filepath}")

    begin_time = perf_counter()

    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_md5.update(chunk)

    end_time = perf_counter()

    logger.debug(f"checked md5 checksum in {end_time - begin_time} seconds")
    return hash_md5.hexdigest()


def check_if_folder_already_contains_file(filepath: str, file_checksum: str):
    """The goal of this function is to check if, in the folder of the filepath provided, it already exists a file with the same checksum as the one provided, with in aim not to download several times the same file. As it's not something required but more of an help for the user, we assume that if the operation takes more than 5 seconds, we abort it."""

    begin_time = perf_counter()

    folder = os.path.dirname(filepath)
    filename = os.path.basename(filepath)

    listdir = [
        name
        for name in os.listdir(folder)
        if not os.path.isdir(os.path.join(folder, name))
    ]  # que les fichiers

    logger.debug(
        f"checking if folder {folder} ({len(listdir)} files) already contains file {filepath}"
    )

    if (
        len(listdir) > FOLDER_CONSIDERED_BIG_SIZE
    ):  # too big folder to test all checksums

        sim_filenames = similar_filenames(
            filename, listdir
        )  # que les noms de fichiers ressemblant, qui ont plus de chance d'avoir le même contenu
        logger.debug(
            f"{folder} folder is too big, checking only files : {sim_filenames}"
        )

        listdir = sim_filenames

    for filename in listdir:
        filepath = os.path.join(folder, filename)

        current_time = perf_counter()
        time_since_begin = current_time - begin_time
        if time_since_begin > MAX_TIME_BEFORE_ABORTING_FOLDER_CHECKSUM:
            return None

        try:
            md5 = compute_md5(filepath)
            if (
                md5 == file_checksum
            ):  # if the current file has the same checksum as the target file
                return filepath

        except PermissionError:
            pass

    return None


def filename_in_folder(name: str, folder_path: str) -> bool:
    """This functions checks if a filename is in a folder

    Parameters
    ----------
    name : str
        the filename
    folder_path : str
        the folder

    Returns
    -------
    bool
        wether the filename exists in the folder
    """
    filename = os.path.join(folder_path, name)
    return file_exists(filename, False)


def filenames_respecting_regex(filenames: List[str], regex: str) -> List[str]:
    """This functions find all the filenames in a list of filenames matching a given regex

    Parameters
    ----------
    filenames : List[str]
        the list of filenames
    regex : str
        the regex

    Returns
    -------
    List[str]
        the filenames matching the regex
    """
    pattern = re.compile(regex)
    return [
        filename for filename in filenames if re.fullmatch(pattern, filename)
    ]
