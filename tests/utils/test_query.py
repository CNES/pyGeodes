from tests.test_case import PyGeodesTestCase
from tests.testutils import random_string, random_int
from tests.serializer import load_serialized_collection, load_serialized_item

from pygeodes.utils.query import (
    Query,
    Argument,
    full_text_search_in_jsons,
    full_text_search,
)


class TestQuery(PyGeodesTestCase):
    def test_instanciation(self):
        q = Query()
        self.assertEqual(q.args, [])

        name = random_string()
        arg = Argument(name)
        self.assertEqual(arg.name, name)

    def test_argument(self):
        arg = Argument(random_string())
        arg.is_in([random_string(), random_string(), random_string()])
        with self.assertRaises(Exception):
            arg.is_in("test")  # not a list
        arg.lte(random_int())
        self.assertEqual(set(arg.to_dict().keys()), {"in", "lte"})

    def test_full_text(self):
        SIZE = 1000
        json = load_serialized_collection(return_obj=False)
        jsons = [json for _ in range(SIZE)]

        search_term = json.get("id")
        results = full_text_search_in_jsons(
            jsons,
            search_term,
            key_field="id",
            fields_to_index={"description", "title", "id"},
        )
        for result in results:
            self.assertTrue(result == json)

        obj = load_serialized_item()
        objs = [obj for _ in range(SIZE)]
        results = full_text_search(objs, obj.id)
        for result in results:
            self.assertTrue(result == obj)

        with self.assertRaises(Exception):
            results = full_text_search(
                [load_serialized_item(), load_serialized_collection()],
                "search_term",
            )
