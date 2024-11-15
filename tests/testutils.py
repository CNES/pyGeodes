import os
import shutil
import random
import datetime
import calendar
import string
from io import StringIO
import sys
from typing import Callable
import subprocess
from pathlib import Path

from tests import (
    VALID_API_KEY_PATH,
    TEST_ENV_DOWNLOAD_DIR,
    TEST_ENV_S3_DOWNLOAD_DIR,
)


def check_presence_of_valid_api_key():
    if not os.path.exists(str(VALID_API_KEY_PATH)):
        raise Exception(
            f"Please provide an api_key at {VALID_API_KEY_PATH} to complete all tests"
        )


def empty_dir(dirpath: Path):
    for element in dirpath.iterdir():
        if os.path.isdir(element):
            shutil.rmtree(element)
        else:
            os.remove(element)


def empty_test_env_download_dir():
    empty_dir(TEST_ENV_DOWNLOAD_DIR)


def empty_test_env_s3_download_dir():
    empty_dir(TEST_ENV_S3_DOWNLOAD_DIR)


def capture_output(function: Callable, args):
    capture = StringIO()
    sys.stdout = capture

    res = function.__call__(**args)

    sys.stdout = sys.__stdout__
    captured = capture.getvalue()
    return res, captured


rd = random.randint


def random_year():
    return rd(1980, 2024)


def random_month():
    return rd(1, 12)


def random_day(year, month):
    return rd(1, calendar.monthrange(year, month)[1])


def random_hour():
    return rd(0, 23)


def random_minute():
    return rd(0, 59)


def random_second():
    return rd(0, 59)


def random_micro_second():
    return rd(0, 999999)


def random_date():
    year = random_year()
    month = random_month()
    day = random_day(year, month)
    hour = random_hour()
    minute = random_minute()
    second = random_second()
    micro_second = random_micro_second()

    return (
        f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}T{str(hour).zfill(2)}:{str(minute).zfill(2)}:{str(second).zfill(2)}.{str(micro_second).zfill(6)}Z",
        datetime.datetime(
            year,
            month,
            day,
            hour=hour,
            minute=minute,
            second=second,
            microsecond=micro_second,
        ),
    )


MAX = 1000


def random_string():
    length = random.randint(1, MAX)
    string_obj = "".join(random.choices(string.printable, k=length))
    return string_obj


def random_int(_max: int = None):
    if _max is None:
        _max = MAX
    return random.randint(1, _max)


def random_float():
    return float(random.random() * MAX)


def random_dict():
    size = random_int()
    dico = {}
    for _ in range(size):
        dico[random_string()] = random.choice(
            [random_string(), random_float(), random_int()]
        )
    return dico


EXAMPLE_COLLECTION_QUERY = {"dataType": {"eq": "PEPS_S1_L1"}}
orbit_down = 50_000
orbit_up = 50_050
EXAMPLE_ITEM_QUERY = {
    "dataType": {"eq": "PEPS_S1_L1"},
    "spaceborne:absoluteOrbitID": {"gte": orbit_down, "lte": orbit_up},
}


def check_collection(collection):
    return collection.id == "PEPS_S1_L1"


def check_item(item):
    orbit = item.find("spaceborne:absoluteOrbitID")
    return (
        item.find("dataType") == "PEPS_S1_L1"
        and orbit >= orbit_down
        and orbit <= orbit_up
    )
