import geopandas as pd

from tests import TEST_ENV_DIR
from tests.test_case import PyGeodesTestCase
from tests.serializer import (
    check_presence_of_serialized_objects,
    load_serialized_collection,
    load_serialized_item,
)
from tests.testutils import random_int, capture_output

from pygeodes.utils.formatting import (
    format_collections,
    format_items,
    export_dataframe,
    load_dataframe,
)


class TestFormatting(PyGeodesTestCase):
    def setUp(self):
        super().setUp()
        check_presence_of_serialized_objects()
        self.collection = load_serialized_collection()
        self.item = load_serialized_item()
        _max = 100
        self.list_of_collections = [
            self.collection for _ in range(random_int(_max))
        ]
        self.list_of_items = [self.item for _ in range(random_int(_max))]

    def test_format_collections_with_query(self):
        query = {"id": {"eq": "PEPS_S1_L1"}}
        formatted = format_collections(
            collections=self.list_of_collections,
            columns_to_add=set(query.keys()),
        )

        self.assertEqual(type(formatted), pd.GeoDataFrame)
        self.assertEqual(formatted.shape[0], len(self.list_of_collections))
        for key in query.keys():
            self.assertTrue(key in formatted.columns)

        self.assertEqual(
            set(formatted["collection"].values), set(self.list_of_collections)
        )

    def test_format_collections_with_custom_columns(self):
        # real_columns
        columns_to_add = {"license", "stac_version"}
        formatted = format_collections(
            collections=self.list_of_collections, columns_to_add=columns_to_add
        )

        self.assertEqual(type(formatted), pd.GeoDataFrame)
        self.assertEqual(formatted.shape[0], len(self.list_of_collections))
        for column in columns_to_add:
            self.assertTrue(column in formatted.columns)
            values = formatted[column].values
            for value in values:
                self.assertTrue(value is not None)

        self.assertEqual(
            set(formatted["collection"].values), set(self.list_of_collections)
        )

        # false columns
        columns_to_add = {"false_column", "123"}
        with self.assertWarns(UserWarning):
            formatted = format_collections(
                collections=self.list_of_collections,
                columns_to_add=columns_to_add,
            )

        self.assertEqual(type(formatted), pd.GeoDataFrame)
        self.assertEqual(formatted.shape[0], len(self.list_of_collections))
        for column in columns_to_add:
            self.assertFalse(column in formatted.columns)

        self.assertEqual(
            set(formatted["collection"].values), set(self.list_of_collections)
        )

    def test_format_items_with_custom_columns(self):
        # real_columns
        columns_to_add = {"temporal:startDate", "spaceborne:swath"}
        formatted = format_items(
            items=self.list_of_items, columns_to_add=columns_to_add
        )

        self.assertEqual(type(formatted), pd.GeoDataFrame)
        self.assertEqual(formatted.shape[0], len(self.list_of_items))
        for column in columns_to_add:
            self.assertTrue(column in formatted.columns)
            values = formatted[column].values
            for value in values:
                self.assertTrue(value is not None)

        self.assertEqual(set(formatted["item"].values), set(self.list_of_items))

        # false columns
        columns_to_add = {"false_column", "123"}
        with self.assertWarns(UserWarning):
            formatted = format_items(
                items=self.list_of_items, columns_to_add=columns_to_add
            )

        self.assertEqual(type(formatted), pd.GeoDataFrame)
        self.assertEqual(formatted.shape[0], len(self.list_of_items))
        for column in columns_to_add:
            self.assertFalse(column in formatted.columns)

        self.assertEqual(set(formatted["item"].values), set(self.list_of_items))

    def test_format_items(self):
        query = {"dataType": {"eq": "PEPS_S1_L1"}}
        formatted = format_items(
            items=self.list_of_items, columns_to_add=set(query.keys())
        )

        self.assertEqual(type(formatted), pd.GeoDataFrame)
        self.assertEqual(formatted.shape[0], len(self.list_of_items))
        for key in query.keys():
            self.assertTrue(key in formatted.columns)

        self.assertEqual(set(formatted["item"].values), set(self.list_of_items))

    def test_format_items_by_adding_columns(self):
        formatted = format_items(
            self.list_of_items, columns_to_add={"dataType"}
        )

        formatted_2 = format_items(
            formatted, columns_to_add={"spaceborne:cloudCover"}
        )
        self.assertTrue(type(formatted_2) is type(formatted))

        for column in ["dataType", "spaceborne:cloudCover", "item"]:
            self.assertTrue(column in formatted_2.columns)

    def test_format_collections_by_adding_columns(self):
        formatted = format_collections(
            self.list_of_collections, columns_to_add={"id"}
        )

        formatted_2 = format_collections(formatted, columns_to_add={"keywords"})
        self.assertTrue(type(formatted_2) is type(formatted))

        for column in ["id", "keywords", "collection"]:
            self.assertTrue(column in formatted_2.columns)

    def test_transtype(self):
        formatted_1 = format_collections(
            self.list_of_collections, columns_to_add={"id"}
        )
        formatted_2 = format_collections(
            self.list_of_collections, columns_to_add=["id"]
        )
        self.assertEqual(set(formatted_1.columns), set(formatted_2.columns))

        formatted_1 = format_items(
            self.list_of_items, columns_to_add={"dataType"}
        )
        formatted_2 = format_items(
            self.list_of_items, columns_to_add=["dataType"]
        )
        self.assertEqual(set(formatted_1.columns), set(formatted_2.columns))

    def test_export_and_load_dataframe(self):
        outfile = str(TEST_ENV_DIR.joinpath("dataframe.json"))
        formatted = format_items(self.list_of_items)
        export_dataframe(formatted, outfile)

        loaded = load_dataframe(outfile)

        self.assertTrue(formatted.equals(loaded))
