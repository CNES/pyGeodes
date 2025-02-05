#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module allows users to configure pygeodes"""
# -----------------------------------------------------------------------------
# Copyright (c) 2024, CNES
#
# REFERENCES:
# https://cnes.fr/
# -----------------------------------------------------------------------------

# stdlib imports -------------------------------------------------------
import sys
import warnings
from dataclasses import asdict, dataclass, fields
from pathlib import Path, PosixPath
from typing import Literal

from pygeodes.utils.consts import (
    CONFIG_DEFAULT_FILENAME,
    DEFAULT_LOGGING_LEVEL,
    DEFAULT_S3_REGION_NAME,
)
from pygeodes.utils.dataclasses_utils import class_from_args
from pygeodes.utils.exceptions import MissingConfParamException

# local imports ---------------------------------------------------
from pygeodes.utils.io import file_exists, load_json
from pygeodes.utils.logger import logger

# third-party imports -----------------------------------------------


def notebook_environment() -> bool:
    """Checks if pygeodes is being used in a notebook environment or not

    Returns
    -------
    bool
        wether we are in a notebook or not
    """
    return "ipykernel" in sys.modules


@dataclass
class Config:
    """This class helps the user configuring Geodes"""

    api_key: str = None  # api_key not always required
    logging_level: Literal["DEBUG", "INFO"] = DEFAULT_LOGGING_LEVEL
    download_dir: str = "."
    checksum_error: bool = True
    use_async_requests: bool = True
    aws_access_key_id: str = None
    aws_secret_access_key: str = None
    aws_session_token: str = None  # ajouter profil à la place
    region_name: str = DEFAULT_S3_REGION_NAME

    @property
    def s3_parameters(self) -> dict:
        """Returns all the conf params related to AWS S3

        Returns
        -------
        dict
            the parameters
        """
        members_names = [
            "aws_access_key_id",
            "aws_secret_access_key",
            "aws_session_token",
            "region_name",
        ]
        return {name: getattr(self, name) for name in members_names}

    def has_s3_parameters(self) -> bool:
        """Returns wether the conf object has s3 parameters with not-None values

        Returns
        -------
        bool
            wether the conf has S3 parameters
        """
        params = self.s3_parameters
        for member_name, value in params.items():
            if value is None:
                return False
        return True

    def check_s3_config(self):
        """Checks if the current conf has s3 parameters

        Raises
        ------
        MissingConfParamException
        """
        params = self.s3_parameters
        for member_name, value in params.items():
            if value is None:
                raise MissingConfParamException(
                    f"To use S3 you need to specify these conf parameters : {', '.join(list(params.keys()))} ({member_name} is None)"
                )

    def to_dict(self) -> dict:
        """Returns the config in Python dict format

        Returns
        -------
        dict
            the config in dict
        """
        return {
            k: str(v) if isinstance(v, PosixPath) else v
            for k, v in asdict(self).items()
        }

    def __post_init__(self):
        """This is executed after creating a Config object, to correct somethings"""
        if self.download_dir is not None:
            self.download_dir = str(Path(self.download_dir).resolve())

        # to deactivate async requests if we are in a notebook environment
        if notebook_environment():
            self.use_async_requests = False

    @property
    def has_api_key(self) -> bool:
        """Returns wether the current config has an api key

        Returns
        -------
        bool
            Returns wether the current config has an api key
        """
        return self.api_key is not None

    @classmethod
    def _check_config_file(cls, content: dict, filepath: str):
        """Opens a filepath to check if its content is suited to load a conf from

        Parameters
        ----------
        content : dict
            the content of the file
        filepath : str
            the filepath of the file
        """
        cls_fields = set([f.name for f in fields(cls) if f.init])
        content_fields = set(content.keys())
        if len(content_fields) > len(cls_fields):
            useless_keys = content_fields - cls_fields
            warnings.warn(
                f"Config file {filepath} contains useless keys ({', '.join(list(useless_keys))})"
            )

    @classmethod
    def _read_info_from_file(cls, file: str):
        """Reads info from a JSON filepath and returns a Config

        Parameters
        ----------
        file : str
            the JSON filepath

        Returns
        -------
        Config
            the config object returned
        """
        content = load_json(file)
        cls._check_config_file(content, file)
        logger.debug(f"Loaded conf from file {file}")
        return class_from_args(Config, content)

    @classmethod
    def from_file(cls, file: str = CONFIG_DEFAULT_FILENAME):
        """Checks if a filepath exists and reads info from a it and returns a Config

        Parameters
        ----------
        file : str, optional
            the filepath, by default CONFIG_DEFAULT_FILENAME

        Returns
        -------
        Config
            the config object
        """
        if file_exists(file, True):
            return cls._read_info_from_file(file)
