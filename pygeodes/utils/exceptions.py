#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module regroups all pygeodes exceptions"""
# -----------------------------------------------------------------------------
# Copyright (c) 2024, CNES
#
# REFERENCES:
# https://cnes.fr/
# -----------------------------------------------------------------------------

# stdlib imports -------------------------------------------------------

# third-party imports -----------------------------------------------

# local imports ---------------------------------------------------


class InvalidURLException(Exception):
    pass


class RequiresApiKeyException(Exception):
    pass


class InvalidChecksumException(Exception):
    pass


class TooManyResultsException(Exception):
    pass


class DataAssetMissingException(Exception):
    pass


class MissingConfParamException(Exception):
    pass
