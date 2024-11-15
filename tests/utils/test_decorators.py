from dataclasses import dataclass

from tests.test_case import PyGeodesTestCase

from pygeodes.utils.decorators import requires_api_key
from pygeodes.utils.config import Config
from pygeodes.utils.exceptions import RequiresApiKeyException


class TestDecorators(PyGeodesTestCase):
    def setUp(self):
        super().setUp()

        class Geodes:
            def __init__(self, conf: Config):
                self.conf = conf

            @requires_api_key
            def method_which_requires_api_key(self):
                pass

            @requires_api_key(bypass_with_s3_credentials=True)
            def method_which_requires_api_key_but_can_be_bypassed_with_s3_credentials(
                self,
            ):
                pass

        self.geodes_class = Geodes

    def test_requires_api_key(self):
        conf_with_api_key = Config(api_key="api_key")

        provider_with_api_key = self.geodes_class(conf=conf_with_api_key)
        provider_with_api_key.method_which_requires_api_key()  # no problem because has api key

        conf_without_api_key = Config()
        provider_without_api_key = self.geodes_class(conf=conf_without_api_key)
        with self.assertRaises(RequiresApiKeyException):
            provider_without_api_key.method_which_requires_api_key()  # problem because hasn't api key

    def test_requires_api_key_s3(self):
        conf_without_api_key_but_with_s3_creds = Config(
            aws_access_key_id="access_key_id",
            aws_secret_access_key="secret_access_key",
            aws_session_token="session_token",
        )
        provider_without_api_key_but_with_s3_creds = self.geodes_class(
            conf=conf_without_api_key_but_with_s3_creds
        )
        provider_without_api_key_but_with_s3_creds.method_which_requires_api_key_but_can_be_bypassed_with_s3_credentials()  # very verbose line, but explicit :)

        conf_without_api_key_nor_s3_creds = Config()
        provider_without_api_key_nor_s3_creds = self.geodes_class(
            conf=conf_without_api_key_nor_s3_creds
        )
        with self.assertRaises(RequiresApiKeyException):
            provider_without_api_key_nor_s3_creds.method_which_requires_api_key_but_can_be_bypassed_with_s3_credentials()
