#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module regroups all the constants from pygeodes"""
# -----------------------------------------------------------------------------
# Copyright (c) 2024, CNES
#
# REFERENCES:
# https://cnes.fr/
# -----------------------------------------------------------------------------

# stdlib imports -------------------------------------------------------
from pathlib import Path

# third-party imports -----------------------------------------------

# local imports ---------------------------------------------------

# geodes
GEODES_DEFAULT_URL = "https://geodes-portal.cnes.fr/"

# datalake
DATALAKE_URL = "https://s3.datalake.cnes.fr/"
DEFAULT_S3_REGION_NAME = "us-east-1"

# config
CONFIG_DEFAULT_FILENAME = "pygeodes-config.json"

# endpoints
GEODES_SEARCH_COLLECTIONS_ENDPOINT = "api/stac/collections"
GEODES_SEARCH_ITEMS_ENDPOINT = "api/stac/search"
GEODES_AVAILABILITY_ENDPOINT = "availability"
GEODES_LIST_PROCESSING_ENDPOINT = "api/processing/processes/"
GEODES_PROCESSING_EXECUTION_ENDPOINT = (
    "api/processing/processes/{process_id}/execution"
)

# requests
# SSL_CERT_PATH = "/etc/pki/tls/cert.pem" #CNES certificate
SSL_CERT_PATH = ""
MAX_PAGE_SIZE = 80
NB_PAGES_LIMIT = 10000000
MAX_NB_ITEMS = MAX_PAGE_SIZE * NB_PAGES_LIMIT
DOWNLOAD_CHUNK_SIZE = 8192
MAX_NB_RETRIES = 5
TIME_BEFORE_RETRY = 2
REQUESTS_TIMEOUT = 10
MAX_TIME_BEFORE_ABORTING_FOLDER_CHECKSUM = 5
MAX_CONCURRENT_DOWNLOADS = 3

# logging
DEFAULT_LOGGING_LEVEL = "INFO"

# STAC
REQUESTABLE_ARGS_FILEPATH = (
    Path(__file__)
    .resolve()
    .parent.parent.joinpath("data")
    .joinpath("model.json")
)
CORRECT_STAC_VERSION = "1.0.0"
KNOWN_COLLECTION_REQUESTABLE_ARGUMENTS = {
    "id",
    "title",
    "keywords",
    "dcs:sensor",
    "dcs:processingLevel",
    "dcs:temporalResolutionInHours",
    "dcs:spatialResolutionInMeters",
    "total_items",
}
KNOWN_ITEM_REQUESTABLE_ARGUMENTS = {
    "dataType",
    "accessService:endpointURL",
    "temporal:startDate",
    "temporal:endDate",
    "spaceborne:orbitID",
    "spaceborne:absoluteOrbitID",
    "spaceborne:orbitDirection",
    "spaceborne:cloudCover",
    "spaceborne:tile",
    "spaceborne:continentsID",
    "spaceborne:satellitePlatform",
    "datetime",
    "spaceborne:sensorMode",
}

# datetime
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
OTHER_SUPPORTED_DATETIME_FORMATS = [
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M",
    "%Y-%m-%dT%H",
    "%Y-%m-%d",
]

# formatting
COLUMNS_TO_KEEP_FORMATTING_COLLECTIONS = {"title", "description"}
COLUMNS_TO_KEEP_FORMATTING_ITEMS = {"id", "collection"}
GEOPANDAS_DEFAULT_EPSG = 4326

# profile
PROFILE_DEFAULT_FOLDER = Path(__file__).parent.parent.joinpath("data")
PROFILE_DEFAULT_PATH = PROFILE_DEFAULT_FOLDER.joinpath("profile.json")

# io
FOLDER_CONSIDERED_BIG_SIZE = 50  # number of files
