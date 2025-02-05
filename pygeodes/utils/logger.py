#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains the pygeodes logger and its config"""
# -----------------------------------------------------------------------------
# Copyright (c) 2024, CNES
#
# REFERENCES:
# https://cnes.fr/
# -----------------------------------------------------------------------------

# stdlib imports -------------------------------------------------------
import logging

# local imports ---------------------------------------------------
from pygeodes.utils.consts import DEFAULT_LOGGING_LEVEL

# third-party imports -----------------------------------------------


logger = logging.getLogger(__name__)
logger.setLevel(DEFAULT_LOGGING_LEVEL)

handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
