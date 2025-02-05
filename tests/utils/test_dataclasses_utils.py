from dataclasses import dataclass

from pygeodes.utils.dataclasses_utils import class_from_args
from tests.test_case import PyGeodesTestCase
from tests.testutils import random_float, random_int, random_string


class TestDataclassesUtils(PyGeodesTestCase):
    def test_class_from_args(self):
        @dataclass
        class ClassExample:
            attr1: str
            attr2: int
            attr3: float
            attr4: str = None

        args = {
            "attr1": random_string(),
            "attr2": random_int(),
            "attr3": random_float(),
        }
        instance = class_from_args(ClassExample, args)
        self.assertTrue(isinstance(instance, ClassExample))

        for attr_name, attr_value in args.items():
            self.assertEqual(getattr(instance, attr_name), attr_value)

        del args["attr1"]
        with self.assertRaises(Exception):  # missing required attr1
            instance = class_from_args(ClassExample, args)
