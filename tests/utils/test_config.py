from pygeodes.utils.config import Config
from pygeodes.utils.exceptions import MissingConfParamException
from tests.test_case import PyGeodesTestCase


class TestConfig(PyGeodesTestCase):
    def test_check_s3_config(self):
        conf = Config()
        with self.assertRaises(MissingConfParamException):
            conf.check_s3_config()

        conf = Config(
            aws_access_key_id="id",
            aws_secret_access_key="key",
            aws_session_token="token",
        )
        conf.check_s3_config()
