from pystac.collection import Collection

from pygeodes.geodes import Geodes
from pygeodes.utils.config import Config
from pygeodes.utils.io import file_exists, load_json, write_json
from pygeodes.utils.stac import Collection, Item
from tests import TEST_ENV_SERIALIZED_DIR, VALID_API_KEY_PATH
from tests.testutils import check_presence_of_valid_api_key

COLLECTION_SERIALIZED_PATH = TEST_ENV_SERIALIZED_DIR.joinpath("collection.json")
ITEM_SERIALIZED_PATH = TEST_ENV_SERIALIZED_DIR.joinpath("item.json")


def load_serialized_collection(return_obj: bool = True) -> Collection:
    content = load_json(str(COLLECTION_SERIALIZED_PATH))
    if return_obj:
        return Collection.from_dict(content)
    else:
        return content


def load_serialized_item(return_obj: bool = True) -> Item:
    content = load_json(str(ITEM_SERIALIZED_PATH))
    if return_obj:
        return Item.from_dict(content)
    else:
        return content


def check_presence_of_serialized_objects():
    if (not file_exists(str(COLLECTION_SERIALIZED_PATH), False)) or (
        not file_exists(str(ITEM_SERIALIZED_PATH), False)
    ):
        raise FileNotFoundError(
            f"Missing serialized collection or item to test, please run {__file__} to solve the problem by serializing a item ({ITEM_SERIALIZED_PATH}) and a collection ({COLLECTION_SERIALIZED_PATH})"
        )


def serialize_an_example_collection(g: Geodes):
    query = {"dataType": {"eq": "PEPS_S1_L1"}}
    print(f"serializing an example collection using query {query}")
    collections = g.search_collections(query=query, raw=True, get_all=False)

    if len(collections) > 0:
        collection = collections[0]
        write_json(collection.to_dict(), str(COLLECTION_SERIALIZED_PATH))
    else:
        print(
            f"Could not serialize any collection, query {query} doesn't return any results !"
        )


def serialize_an_example_item(g: Geodes):
    query = {"dataType": {"eq": "PEPS_S1_L1"}}
    print(f"serializing an example item using query {query}")
    items = g.search_items(query=query, raw=True, get_all=False)

    if len(items) > 0:
        item = items[0]
        write_json(item.to_dict(), str(ITEM_SERIALIZED_PATH))
    else:
        print(
            f"Could not serialize any item, query {query} doesn't return any results !"
        )


if __name__ == "__main__":
    check_presence_of_valid_api_key()
    valid_api_key = load_json(str(VALID_API_KEY_PATH))["api_key"]

    conf = Config(api_key=valid_api_key)
    geodes = Geodes(conf=conf)

    serialize_an_example_collection(geodes)
    serialize_an_example_item(geodes)
