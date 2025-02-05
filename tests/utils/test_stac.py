from pygeodes.geodes import Geodes
from pygeodes.utils.config import Config
from pygeodes.utils.exceptions import DataAssetMissingException
from pygeodes.utils.stac import Collection, Item
from tests.serializer import load_serialized_collection, load_serialized_item
from tests.test_case import PyGeodesTestCase


class TestSTAC(PyGeodesTestCase):
    def setUp(self):
        super().setUp()
        self.item_json = load_serialized_item(return_obj=False)
        self.collection_json = load_serialized_collection(return_obj=False)
        self.item = Item.from_dict(self.item_json)
        self.collection = Collection.from_dict(self.collection_json)

    def test_from_dict(self):
        self.assertEqual(self.item.to_dict(), self.item_json)

        self.assertEqual(self.collection.to_dict(), self.collection_json)

    def test_find(self):
        for prop, value in self.item.properties.items():
            if not type(value) in [
                list,
                dict,
            ]:  # Item.find() doesn't work with lists and dicts
                self.assertEqual(value, self.item.find(prop))

    def test_data_asset(self):
        self.assertTrue(self.item.data_asset is not None)

        data_asset_key = None
        for key, asset in self.item.assets.items():
            if "data" in asset.roles:
                data_asset_key = key

        if data_asset_key is not None:
            del self.item.assets[data_asset_key]

        with self.assertRaises(DataAssetMissingException):
            _ = self.item.data_asset

    def test_misc(self):
        self.assertEqual(self.item.filesize, self.item.data_asset.filesize)
        self.assertEqual(type(self.item.data_asset.filesize), int)

    def test_list_keys(self):
        keys = self.item.list_available_keys()
        self.assertTrue(type(keys) is set)
        for key in keys:
            self.assertFalse(self.item.find(key) is None)

        keys = self.collection.list_available_keys()
        self.assertTrue(type(keys) is set)
        for key in keys:
            self.assertFalse(self.collection.find(key) is None)
