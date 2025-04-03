#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module deals with all things related to Amazon S3"""
# -----------------------------------------------------------------------------
# Copyright (c) 2024, CNES
#
# REFERENCES:
# https://cnes.fr/
# -----------------------------------------------------------------------------

# stdlib imports -------------------------------------------------------
import warnings

# third-party imports -----------------------------------------------
import boto3
from botocore.client import Config as botocore_config

# local imports ---------------------------------------------------
from pygeodes.utils.config import Config
from pygeodes.utils.consts import DATALAKE_URL
from pygeodes.utils.io import check_if_folder_already_contains_file
from pygeodes.utils.logger import logger
from pygeodes.utils.stac import Item


def create_boto3_client(conf: Config):
    conf.check_s3_config()

    parameters = conf.s3_parameters
    parameters["endpoint_url"] = DATALAKE_URL
    parameters["config"] = botocore_config(signature_version="s3v4")

    client = boto3.client("s3", **parameters)
    return client


def get_bucket_and_key_from_url(url: str):
    url = url.replace(DATALAKE_URL, "")
    split = url.split("/")
    bucket = split[0]
    key = "/".join(split[1:])
    return bucket, key


def download_item(client, item: Item, outfile: str):
    name_for_same_file = check_if_folder_already_contains_file(
        outfile, item.data_asset.checksum
    )

    if name_for_same_file is not None:
        warnings.warn(
            f"trying to download content at {outfile} but file with same content already exists in the same folder at {name_for_same_file}, skipping download"
        )
        return name_for_same_file

    url = item.find("endpoint_url") # TODO: check
    bucket, key = get_bucket_and_key_from_url(url)
    logger.debug(f"using {bucket=} and {key=}")
    client.download_file(Bucket=bucket, Key=key, Filename=outfile)
    print(f"Download from s3 completed at {outfile}")
    return outfile
