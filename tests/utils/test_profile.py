from copy import deepcopy
from datetime import timedelta

from pygeodes.geodes import Geodes
from pygeodes.utils.config import Config
from pygeodes.utils.io import file_exists
from pygeodes.utils.profile import Download, DownloadQueue, Profile
from tests import TEST_ENV_DOWNLOAD_DIR
from tests.test_case import PyGeodesTestCase
from tests.testutils import (
    EXAMPLE_ITEM_QUERY,
    empty_test_env_download_dir,
    random_date,
)


class TestProfile(PyGeodesTestCase):
    def test_instanciation(self):
        profile = Profile.load()
        self.assertEqual(type(profile.downloads), dict)
        pass

    def test_reset(self):
        Profile.reset()
        self.assertFalse(file_exists(Profile._filepath, False))
        profile = Profile.load()
        self.assertEqual(type(profile.downloads), dict)
        self.assertTrue(file_exists(Profile._filepath, False))

    def test_to_dict(self):
        Profile.reset()
        profile = Profile.load()
        self.assertEqual(profile.to_dict().get("nb_downloads"), 0)
        self.assertEqual(
            profile.to_dict().get("nb_downloads"), len(profile.downloads)
        )
        _, started_at = random_date()
        completed_at = started_at + timedelta(seconds=10)
        d = Download(
            url="path/to/download.com",
            destination="/path/to/file.txt",
            _started_at=started_at,
            _completed_at=completed_at,
        )
        profile.add_download(d)
        profile.save()

        profile = Profile.load()
        self.assertEqual(profile.to_dict().get("nb_downloads"), 1)
        self.assertEqual(
            profile.to_dict().get("nb_downloads"), len(profile.downloads)
        )
        self.assertEqual(profile.downloads[d._id], d)

    def test_download(self):
        Profile.reset()
        _, started_at = random_date()
        completed_at = started_at + timedelta(seconds=10)
        d = Download(
            url="path/to/download.com",
            destination="/path/to/file.txt",
            _started_at=started_at,
            _completed_at=completed_at,
        )

        profile = Profile.load()
        profile.add_download(d)
        profile.save()

        self.assertTrue(d in profile.downloads.values())

        downloads = deepcopy(
            profile.downloads
        )  # to avoid references in the future

        profile.add_download(d)

        self.assertEqual(
            profile.downloads, downloads
        )  # because adding the same download should change nothing as it's already registered

        d.destination = "/other/path"
        profile.add_download(d)

        self.assertNotEqual(profile.downloads.values(), downloads.values())

    def test_download_queue(self):
        NB_DOWNLOADS = 5

        Profile.reset()

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
        items = [
            item
            for item, filesize in sorted(filesizes, key=lambda tp: tp[1])[
                :NB_DOWNLOADS
            ]
        ]

        queue = DownloadQueue(items=items)
        self.assertEqual(queue.items, items)
        self.assertEqual(queue.downloads_objects, {})
        self.assertEqual(queue.geodes_instance, geodes)
        self.assertEqual(queue.download_dir, geodes.conf.download_dir)

        queue._init_downloads()
        profile = Profile.load()

        for item in items:
            download = queue.downloads_objects.get(item)
            self.assertEqual(download.url, item.data_asset.href)
            self.assertEqual(download.destination, None)
            self.assertTrue(download._started_at is None)
            self.assertTrue(download == profile.downloads.get(download._id))

        for item in items:
            queue._download_item(item)

        profile = Profile.load()
        for item in items:
            download = queue.downloads_objects.get(item)
            self.assertTrue(download == profile.downloads.get(download._id))
            self.assertTrue(download.completed_at is not None)

        empty_test_env_download_dir()
