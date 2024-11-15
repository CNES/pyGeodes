import os

from tests.test_case import PyGeodesTestCase
from tests import TEST_ENV_DIR
from tests.testutils import random_dict

from pygeodes.utils.io import (
    file_exists,
    filenames_respecting_regex,
    filename_in_folder,
    find_unused_filename,
    similar_filenames,
    write_json,
    load_json,
)


def write_empty_file(path: str):
    with open(path, "w") as file:
        file.write("")


class TestIO(PyGeodesTestCase):
    def tearDown(self):
        for filepath in TEST_ENV_DIR.joinpath(
            "test_folder"
        ).iterdir():  # for cleanup
            os.remove(filepath)
        super().tearDown()

    def test_file_exists(self):
        filename = "file.txt"
        filepath = TEST_ENV_DIR.joinpath("test_folder").joinpath(filename)

        write_empty_file(filepath)

        self.assertTrue(file_exists(filepath))

        os.remove(filepath)

        with self.assertRaises(FileNotFoundError):
            file_exists(filepath)

        self.assertFalse(file_exists(filepath, False))

    def test_find_unused_filename(self):
        filepath = str(
            TEST_ENV_DIR.joinpath("test_folder").joinpath("filename.txt")
        )

        NB_FILES = 30

        self.assertEqual(
            filepath, find_unused_filename(filepath)
        )  # as there is no other

        to_delete = []
        write_empty_file(filepath)
        to_delete.append(filepath)

        for index in range(1, NB_FILES):
            new_filepath = str(
                TEST_ENV_DIR.joinpath("test_folder").joinpath(
                    f"filename-{index}.txt"
                )
            )
            self.assertEqual(new_filepath, find_unused_filename(filepath))
            write_empty_file(new_filepath)
            to_delete.append(new_filepath)

    def test_filename_in_folder(self):
        folder = TEST_ENV_DIR.joinpath("test_folder")
        name = "file.txt"
        filepath = folder.joinpath(name)
        write_empty_file(filepath)

        self.assertTrue(filename_in_folder(name, folder))

        os.remove(str(filepath))

        self.assertFalse(filename_in_folder(name, folder))

    def test_json_io(self):
        dico = random_dict()
        filepath = str(
            TEST_ENV_DIR.joinpath("test_folder").joinpath("file.json")
        )
        write_json(dico, filepath)
        self.assertTrue(file_exists(filepath))

        self.assertEqual(dico, load_json(filepath))

    def test_similar_filenames(self):
        filename = "filename.txt"
        other_filenames = [
            "fileName.txt",
            "FiLeName.TxT",
            "FiiiileName.txt",
            "filename.tx",
            " filename.txt",
            "not_looking_like_the_other_filename.json",
            "QuiteDifferentFile.jpg",
            "nothing_to_do.py",
        ]
        self.assertEqual(
            set(other_filenames[:5]),
            set(similar_filenames(filename, other_filenames, nb=5)),
        )  # we turn it into a set because we can't predict the ordering of the output list of files, we just can say that the first 4 filenames are the most resembling

    def test_filenames_respecting_regex(self):
        regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"  # email address regex
        filenames = [
            "test@cnes.fr",
            "email.address@domain.com",
            "not_an_email_address",
        ]
        self.assertEqual(
            filenames_respecting_regex(filenames, regex), filenames[:2]
        )

        filenames = [
            "definitely not an email address",
            "anotherBadExample",
            "this.one.is@nearlyGoodButNot",
        ]
        self.assertEqual(filenames_respecting_regex(filenames, regex), [])
