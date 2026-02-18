#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_geodes.py

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
from datetime import datetime
from time import perf_counter

# third-party imports -----------------------------------------------
import geopandas as pd

from pygeodes.geodes import Geodes
from pygeodes.utils.config import Config
from pygeodes.utils.exceptions import (
    InvalidURLException,
    RequiresApiKeyException,
)
from pygeodes.utils.io import file_exists
from pygeodes.utils.logger import logger
from pygeodes.utils.profile import Download, Profile
from pygeodes.utils.stac import Collection, Item
from tests import TEST_ENV_DOWNLOAD_DIR

# local imports ---------------------------------------------------
from tests.test_case import PyGeodesTestCase
from tests.testutils import (
    EXAMPLE_COLLECTION_QUERY,
    EXAMPLE_ITEM_QUERY,
    EXAMPLE_SORTBY,
    check_collection,
    check_item,
    empty_test_env_download_dir,
)


class TestGeodes(PyGeodesTestCase):
    def setUp(self):
        super().setUp()
        self.collection_query = EXAMPLE_COLLECTION_QUERY
        self.item_query = EXAMPLE_ITEM_QUERY
        self.sortBy = EXAMPLE_SORTBY
        self.download_dir = TEST_ENV_DOWNLOAD_DIR
        self.valid_conf = Config(
            api_key=self.valid_api_key,
            download_dir=str(self.download_dir),
        )
        self.valid_geodes = Geodes(conf=self.valid_conf)
        logger.setLevel("INFO")

    def tearDown(self):
        empty_test_env_download_dir()
        super().tearDown()

    def test_simple_instanciation(self):
        g = Geodes()
        self.assertEqual(g.conf, Config())

    def test_instanciation_with_conf_from_path(self):
        conf = Config.from_file(str(self.other_config_file))
        g = Geodes(conf=conf)

    def test_instanciation_with_manual_conf(self):
        conf = Config(api_key="api_key")
        g = Geodes(conf=conf)

    def test_instanciation_with_custom_url(self):
        g = Geodes(base_url="https://valid.url.com/", conf=self.valid_conf)

    def test_instanciation_with_invalid_url(self):
        with self.assertRaises(InvalidURLException):
            g = Geodes(base_url="https:/valid.url.com/", conf=self.valid_conf)

    def test_instanciation_request_maker(self):
        rq_maker = self.valid_geodes.request_maker
        self.assertEqual(rq_maker.api_key, self.valid_geodes.conf.api_key)
        self.assertEqual(rq_maker.base_url, self.valid_geodes.base_url)

    def test_search_collections(self):
        geodes = self.valid_geodes
        collections, dataframe = geodes.search_collections(
            query=self.collection_query, return_df=True
        )
        print(f"{collections=}")
        self.assertEqual(type(collections), list)

        for collection in collections:
            self.assertEqual(type(collection), Collection)
            self.assertTrue(
                check_collection(collection)
            )  # depends on the query

        self.assertEqual(type(dataframe), pd.GeoDataFrame)
        for key in self.collection_query.keys():
            if key == "dataset":
                key = "id"
            self.assertTrue(key in dataframe.columns)

    def test_search_items(self):
        geodes = self.valid_geodes

        items, dataframe = geodes.search_items(
            get_all=False,
            query=self.item_query,
            return_df=True,
        )

        self.assertEqual(type(items), list)
        for item in items:
            self.assertEqual(type(item), Item)
            self.assertTrue(check_item(item))

        self.assertEqual(type(dataframe), pd.GeoDataFrame)
        for key in self.item_query.keys():
            self.assertTrue(key in dataframe.columns)

    def test_search_items_async(self):
        geodes = self.valid_geodes

        async_begin = perf_counter()

        async_items = geodes.search_items(
            get_all=True, query=self.item_query, sortBy=self.sortBy, return_df=False
        )  # by default, get_all will use async requests

        async_end = perf_counter()
        async_time = async_end - async_begin

        self.assertEqual(type(async_items), list)
        for item in async_items:
            self.assertEqual(type(item), Item)
            self.assertTrue(check_item(item))

        geodes.conf.use_async_requests = False

        sync_begin = perf_counter()

        sync_items = geodes.search_items(
            get_all=True, query=self.item_query, sortBy=self.sortBy, return_df=False
        )  # as we changed the parameter in conf, it will use sync requests

        sync_end = perf_counter()
        sync_time = sync_end - sync_begin

        self.assertEqual(type(sync_items), list)
        for item in sync_items:
            self.assertEqual(type(item), Item)
            self.assertTrue(check_item(item))

        sync_items = set([item.id for item in sync_items])
        async_items = set([item.id for item in async_items])

        self.assertEqual(sync_items, async_items)
        print(
            f"{sync_time=} | {async_time=} for {len(async_items)} items found"
        )

        self.assertTrue(
            async_time < sync_time,
            f"async is not faster than sync {sync_time=} < {async_time=}",
        )

    def test_download_item_archive(self):
        items = self.valid_geodes.search_items(
            get_all=False, query=self.item_query, sortBy=self.sortBy, return_df=False
        )  # hoping this request returns at least one product

        filesizes = [(item, item.data_asset.filesize) for item in items]
        filesizes_sorted = sorted(filesizes, key=lambda tp: tp[1])

        smallest_item = filesizes_sorted[0][0]
        second_smallest_item = filesizes_sorted[1][0]

        g = Geodes(conf=Config(api_key=None, checksum_error=False))

        with self.assertRaises(RequiresApiKeyException):
            g.download_item_archive(smallest_item)

        empty_test_env_download_dir()

        Profile.reset()  # for testing

        begin_download = datetime.now()

        # without specifying a name for the outfile
        self.valid_geodes.download_item_archive(smallest_item)

        end_download = datetime.now()

        outfile = self.download_dir.joinpath(smallest_item.data_asset.title)
        self.assertTrue(file_exists(outfile))
        profile = Profile.load()
        download = list(profile.downloads.values())[0]
        self.assertEqual(download.destination, str(outfile))
        self.assertTrue(begin_download < download.started_at < end_download)
        self.assertTrue(
            download.started_at < download.completed_at < end_download
        )

        os.remove(str(outfile))

        # specifying a name for the outfile
        outfile = "outfile.zip"
        self.valid_geodes.download_item_archive(smallest_item, outfile)
        self.assertTrue(file_exists(self.download_dir.joinpath(outfile)))

        # specifying the same name two times in the same folder
        outfile = "outfile.zip"
        self.valid_geodes.download_item_archive(second_smallest_item, outfile)
        self.assertTrue(
            file_exists(self.download_dir.joinpath("outfile-1.zip"))
        )

        empty_test_env_download_dir()

    def test_list_item_files_and_download_file(self):
        items = self.valid_geodes.search_items(
            get_all=False, query=self.item_query, sortBy=self.sortBy, return_df=False
        )

        item = items[0]
        list_files = self.valid_geodes.list_item_files(item)
        self.assertEqual(type(list_files), list)
        for file in list_files:
            self.assertEqual(type(file), str)

        self.valid_geodes.download_item_files(
            item, filenames=[list_files[1], list_files[2]]
        )  # nothing to assert except it works ok, for now

    @unittest.skip(
        "skipping test_check_item_availability as availability is not already available on prod"
    )
    def test_check_item_availability(self):
        items = self.valid_geodes.search_items(
            get_all=False, query=self.item_query, return_df=False
        )
        item = items[0]
        avai = self.valid_geodes.check_item_availability(item)

    @unittest.skip(
        "skipping test_list_available_processes as it is not completely implemented yet"
    )
    def test_list_available_processes(self):
        processes = self.valid_geodes.list_available_processes()
        self.assertTrue(type(processes) is list)

        processes = self.valid_geodes.list_available_processes(raw=True)
        self.assertTrue(type(processes) is dict)
