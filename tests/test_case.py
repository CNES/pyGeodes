#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_case.py

[your module's docstring]

"""
# -----------------------------------------------------------------------------
# Copyright (c) 2024, CNES
#
# REFERENCES:
# https://cnes.fr/
# -----------------------------------------------------------------------------

import os

# stdlib imports -------------------------------------------------------
import unittest

from pygeodes.utils.io import load_json

# local imports ---------------------------------------------------
from pygeodes.utils.logger import logger
from tests import TEST_ENV_DIR, TESTS_DIR, VALID_API_KEY_PATH
from tests.testutils import check_presence_of_valid_api_key

# third-party imports -----------------------------------------------


class PyGeodesTestCase(unittest.TestCase):
    def setUp(self):
        check_presence_of_valid_api_key()
        self.valid_api_key = load_json(VALID_API_KEY_PATH)["api_key"]

        self.other_config_file = TEST_ENV_DIR.joinpath(
            "other-config-file.json"
        )
        os.chdir(
            str(TEST_ENV_DIR)
        )  # to make python act as if we were executing from test_env folder
        pass

    def tearDown(self):
        pass
