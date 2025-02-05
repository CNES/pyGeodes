import unittest
from time import perf_counter

from tqdm import tqdm

from pygeodes.geodes import Geodes
from pygeodes.utils.config import Config
from pygeodes.utils.consts import (
    GEODES_DEFAULT_URL,
    GEODES_SEARCH_COLLECTIONS_ENDPOINT,
    GEODES_SEARCH_ITEMS_ENDPOINT,
)
from pygeodes.utils.download import correct_download_tld
from pygeodes.utils.io import file_exists
from pygeodes.utils.request import (
    AsyncRequestMaker,
    SyncRequestMaker,
    make_params,
)
from pygeodes.utils.stac import Collection, Item
from tests import TEST_ENV_DOWNLOAD_DIR
from tests.test_case import PyGeodesTestCase
from tests.testutils import EXAMPLE_ITEM_QUERY, empty_test_env_download_dir


class TestRequest(PyGeodesTestCase):
    def setUp(self):
        super().setUp()
        api_key = self.valid_api_key
        base_url = GEODES_DEFAULT_URL
        self.sync_rqm = SyncRequestMaker(api_key=api_key, base_url=base_url)
        self.async_rqm = AsyncRequestMaker(api_key=api_key, base_url=base_url)

    def test_post_sync(self):
        response = self.sync_rqm.post(
            endpoint=GEODES_SEARCH_COLLECTIONS_ENDPOINT,
            data=make_params(page=1, query={"dataType": {"contains": "PEPS"}}),
        )
        self.assertTrue(response.ok)
        self.assertTrue("collections" in response.json().keys())
        self.assertEqual(type(response.json().get("collections")), list)

    def tearDown(self):
        empty_test_env_download_dir()
        super().tearDown()

    def test_async_download(self):
        NB_DOWNLOADS = 10

        geodes = Geodes(
            conf=Config(
                api_key=self.valid_api_key,
                download_dir=str(TEST_ENV_DOWNLOAD_DIR),
            )
        )
        items = geodes.search_items(
            get_all=False, query=EXAMPLE_ITEM_QUERY, return_df=False
        )

        filesizes = [(item, item.data_asset.filesize) for item in items]
        smallests = [
            item
            for item, filesize in sorted(filesizes, key=lambda tp: tp[1])[
                :NB_DOWNLOADS
            ]
        ]
        endpoints = [
            correct_download_tld(item.data_asset.href) for item in smallests
        ]
        outfiles = [
            str(TEST_ENV_DOWNLOAD_DIR.joinpath(item.data_asset.title))
            for item in smallests
        ]
        checksums = [item.data_asset.checksum for item in smallests]

        begin = perf_counter()

        self.async_rqm.download_files(endpoints, outfiles, checksums)

        end = perf_counter()
        async_time = end - begin

        for outfile in outfiles:
            self.assertTrue(file_exists(outfile))

        empty_test_env_download_dir()

        begin = perf_counter()

        for item in smallests:
            geodes.download_item_archive(item)

        end = perf_counter()
        sync_time = end - begin

        print(
            f"{sync_time=} | {async_time=} for {NB_DOWNLOADS=} (filesize total = {sum([item.filesize for item in smallests])})"
        )
        self.assertTrue(sync_time > async_time)

    def test_comparison_post_collections(self):
        NB_REQUESTS = 5
        params = make_params(page=1, query={"total_items": {"gte": "0"}})

        # sync
        sync_responses = []
        sync_begin = perf_counter()

        for _ in tqdm(range(NB_REQUESTS)):
            response = self.sync_rqm.post(
                endpoint=GEODES_SEARCH_COLLECTIONS_ENDPOINT, data=params
            )
            sync_responses.append(response.json())

        sync_end = perf_counter()
        time_sync = sync_end - sync_begin

        sync_collections = set()
        for resp_json in sync_responses:
            sync_collections.update(
                {
                    Collection.from_dict(dico).id
                    for dico in resp_json.get("collections")
                }
            )

        # async
        async_begin = perf_counter()

        async_responses = self.async_rqm.post(
            endpoints=[
                GEODES_SEARCH_COLLECTIONS_ENDPOINT for _ in range(NB_REQUESTS)
            ],
            headers=[None for _ in range(NB_REQUESTS)],
            datas=[params for _ in range(NB_REQUESTS)],
        )

        async_end = perf_counter()
        time_async = async_end - async_begin

        async_collections = set()
        for resp_json in async_responses:
            async_collections.update(
                {
                    Collection.from_dict(dico).id
                    for dico in resp_json.get("collections")
                }
            )

        self.assertEqual(
            async_collections, sync_collections
        )  # to ensure we get the same results
        self.assertTrue(
            time_sync > time_async
        )  # to ensure it's faster in async
        print(
            f"{time_sync=} | {time_async=} for {NB_REQUESTS=} ({len(async_collections)} collections found)"
        )

    def test_comparison_post_items(self):
        NB_REQUESTS = 10
        params = make_params(page=1, query={"dataType": {"contains": "PEPS"}})

        # sync
        sync_responses = []
        sync_begin = perf_counter()

        for _ in tqdm(range(NB_REQUESTS)):
            response = self.sync_rqm.post(
                endpoint=GEODES_SEARCH_ITEMS_ENDPOINT, data=params
            )
            sync_responses.append(response.json())

        sync_end = perf_counter()
        time_sync = sync_end - sync_begin

        sync_items = set()
        for resp_json in sync_responses:
            sync_items.update(
                {Item.from_dict(dico).id for dico in resp_json.get("features")}
            )

        # async
        async_begin = perf_counter()

        async_responses = self.async_rqm.post(
            endpoints=[
                GEODES_SEARCH_ITEMS_ENDPOINT for _ in range(NB_REQUESTS)
            ],
            headers=[None for _ in range(NB_REQUESTS)],
            datas=[params for _ in range(NB_REQUESTS)],
        )

        async_end = perf_counter()
        time_async = async_end - async_begin

        async_items = set()
        for resp_json in async_responses:
            async_items.update(
                {Item.from_dict(dico).id for dico in resp_json.get("features")}
            )

        self.assertEqual(
            async_items, sync_items
        )  # to ensure we get the same results
        self.assertTrue(
            time_sync > time_async
        )  # to ensure it's faster in async
        print(
            f"{time_sync=} | {time_async=} for {NB_REQUESTS=} ({len(async_items)} items found)"
        )
