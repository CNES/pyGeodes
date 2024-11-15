Unit testing
============

Intro
-----

There are many unit tests in |pn| to ensure all of its features are working fine.
The framework used is Python's built-in one, unittest_.

.. _unittest: https://docs.python.org/3/library/unittest.html

The framework uses classes to make tests, this system allows the developer to add inheritance to the tests.

In |pn|, all tests inherit from the ``PyGeodesTestCase`` class.

Develop new tests
-----------------

The tests files architecture is designed to mirror the source one : the tests for a ``foo`` module in ``pygeodes/utils/foo.py`` are in ``tests/utils/test_foo.py``.
A test module is just a class, which inherits from ``PyGeodesTestCase``. The methods will be the tests, let's see an example : 

.. code-block:: python

    import random

    from pygeodes.tests.test_case import PyGeodesTestCase
    from pygeodes.utils.foo import multiply_by_two
    
    class FooTestCase(PyGeodesTestCase):
        def test_multiply_by_two(self):
            number = random.randint(1,100)
            self.assertEqual(number * 2,multiply_by_two(number))

            # or 

            self.assertTrue(number * 2 == multiply_by_two(number))

Use of ``setUp`` and ``tearDown`` methods
-----------------------------------------

``unittest`` provides the ``setUp`` and ``tearDown`` methods, which are very useful.

``setUp``
^^^^^^^^^

The ``setUp`` method is executed before each test in a class. There is a general ``setUp`` method in the implementation of ``PyGeodesTestCase``, but you can develop a new one, adapted to your test_case, which inherits from the original one ``setUp``.
Here's an example, let's keep up with our ``FooTestCase`` defined previously :

.. code-block:: python

    # imports ...
    from pygeodes.utils.foo import multiply_by_two,multiply_by_three

    
    class FooTestCase(PyGeodesTestCase):

        def setUp(self):
            super().setUp() # use first the one from the super class
            
            # define your own behaviour
            self.random_number = random.randint(1,100)

        def test_multiply_by_two(self):
            self.assertEqual(self.random_number * 2,multiply_by_two(self.random_number))

        def test_multiply_by_three(self):
            self.assertEqual(self.random_number * 3,multiply_by_three(self.random_number))

A new random number is generated at each execution and before each test !

``tearDown``
^^^^^^^^^^^^

``tearDown`` acts like ``setUp`` but *after* each method, not *before*.
An example of good use could be : 

.. code-block:: python

    # imports ...
    from pygeodes.utils.file_io import ...

    class FileIOTestCase(PyGeodesTestCase):

        def setUp(self):
            super().setUp() # use first the one from the super class
            
            self.file = open("file.txt")

        def test_some_method_on_file(self):
            ...

        def test_some_other_method_on_file(self):
            ...

        def tearDown(self):
            self.file.close()
        
            super().tearDown() # use last the one from the super class
            

.. seealso::

   For further details about *unittest*, see the docs_
   
   .. _docs: https://docs.python.org/3/library/unittest.html

Run your tests
--------------

To run your new tests, you can start a new test session using the makefile commands (see :doc:`makefile`).

.. hint::

   In order to validate some tests, you need to provide a real Geodes api key, which must be put under the format ``{"api_key" : "your_api_key"}`` in ``tests/valid-api-key.json``. 

Specific tests
--------------

Some tests use pre-serialized STAC collections and items (in order not to make a request to geodes each time you make a test involving a STAC collection or a STAC item), which can be written in the folder ``pygeodes/tests/test_env/serialized`` as ``collection.json`` and ``item.json``.
The script ``pygeodes/tests/serializer.py`` can be used to serialize these json objects from a request to geodes.
In case you would start a test which requires those files without them being in ``pygeodes/tests/test_env/serialized``, you would come across an Exception telling you to use ``pygeodes/tests/serializer.py``.

