from pygeodes.utils.datetime_utils import (
    datetime_to_str,
    str_to_datetime,
    complete_datetime_from_str,
)

from tests.test_case import PyGeodesTestCase
from tests.testutils import random_date
from pygeodes.utils.consts import (
    DATETIME_FORMAT,
    OTHER_SUPPORTED_DATETIME_FORMATS,
)


class TestDatetimeUtils(PyGeodesTestCase):
    def test_datetime_to_str(self):
        NB_TESTS = 10000  # to test various configurations

        for _ in range(NB_TESTS):
            string, datetime_obj = random_date()
            to_str = datetime_to_str(datetime_obj)
            self.assertEqual(to_str, string)

    def test_str_to_datetime(self):
        NB_TESTS = 10000  # to test various configurations

        for _ in range(NB_TESTS):
            string, datetime_obj = random_date()
            datetime_obj_from_str = str_to_datetime(string)
            self.assertEqual(datetime_obj_from_str, datetime_obj)

    def test_complete_datetime(self):
        NB_TESTS = 10000
        for _ in range(NB_TESTS):
            _, date = random_date()
            for fmt in OTHER_SUPPORTED_DATETIME_FORMATS:
                date_fmt = date.strftime(fmt)
                completed = complete_datetime_from_str(date_fmt)
