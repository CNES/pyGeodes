import unittest

from tests import TEST_ENV_DOWNLOAD_DIR, TEST_ENV_S3_DOWNLOAD_DIR
from tests.test_case import PyGeodesTestCase
from tests.testutils import (
    empty_test_env_download_dir,
    empty_test_env_s3_download_dir,
)
from tests.serializer import load_serialized_item

from pygeodes.utils.s3 import create_boto3_client, download_item
from pygeodes.utils.config import Config
from pygeodes.utils.io import file_exists, compute_md5
from pygeodes.geodes import Geodes

# CREDENTIALS = get_s3_credentials()


class TestS3(PyGeodesTestCase):
    def tearDown(self):
        empty_test_env_download_dir()
        empty_test_env_s3_download_dir()
        super().tearDown()

    def test_with_wrong_credentials(self):
        conf = Config(
            aws_access_key_id="id",
            aws_secret_access_key="key",
            aws_session_token="token",
        )
        client = create_boto3_client(conf)
        with self.assertRaises(Exception):
            buckets = client.list_buckets()

    @unittest.skip("can't be tested without valid credentials")
    def test_create_boto3_client(self):
        conf = Config(**CREDENTIALS)
        client = create_boto3_client(conf)

        buckets = client.list_buckets()["Buckets"]
        self.assertTrue(type(buckets), list)
        for bck in buckets:
            self.assertTrue(type(bck), dict)

        item = load_serialized_item()
        real_checksum = item.data_asset_checksum
        s3_outfile = TEST_ENV_S3_DOWNLOAD_DIR.joinpath(
            "from_s3.zip"
        )  # can't put it directly in download_dir
        # because when we will download the other file, it will raise an error saying there are two files with the same checksum in the download_dir directory

        download_item(client, item, s3_outfile)
        self.assertTrue(file_exists(s3_outfile))
        s3_md5 = compute_md5(s3_outfile)
        self.assertTrue(real_checksum, s3_md5)

        conf = Config(
            api_key=self.valid_api_key,
            download_dir=TEST_ENV_DOWNLOAD_DIR,
        )

        classic_outfile = TEST_ENV_DOWNLOAD_DIR.joinpath("classic.zip")

        geodes = Geodes(conf=conf)
        geodes.download_item_archive(item, outfile=classic_outfile)
        self.assertTrue(s3_md5, compute_md5(classic_outfile))
