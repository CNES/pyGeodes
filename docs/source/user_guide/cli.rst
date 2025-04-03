Command-line interface (CLI)
============================

|pn| also comes out with a CLI_ which you can use as an alternative to the programmatical version of |pn|.

.. _CLI: https://en.wikipedia.org/wiki/Command-line_interface

Getting started
---------------

To get started, make sure you installed |pn| (see :doc:`installation`). To check that your installation is ok, run : 

.. code-block:: bash

    pygeodes --version

If it outputs a version number, you're good to go !

.. _searching_items:
Searching items
---------------

The command line let's you search for items, which you can do by using the command ``search``, whose options are : 

-cs, --collections_search     wether to search in collections instead of items
--start-date START_DATE
                    the lower bound of the acquisition date of the item you want to search
--end-date END_DATE   the upper bound of the acquisition of the item you want to search
--data-type DATA_TYPE
                    the data type of the item you want to search
-q QUERY, --query QUERY
                    the search query you want to use, it can be a filepath to a json or a json directly in the command
-b BBOXBBOXBBOXBBOX, --bbox BBOXBBOXBBOXBBOX
                    a bounding box in which you could want to search, e.g. : 1.3 44.6 2.1 44.9
-o OUTPUT, --output OUTPUT
                    the json file to export the results to, if not specified results will just be displayed
-c COLLECTIONS, --collections COLLECTIONS
                    the collection of the item you want to search

For example, to search items in bbox ``[1.3,44.6,2.1,44.9]`` whose acquisition date is before the 29th of January, 2006, you can use :

.. code-block:: bash

    pygeodes search --bbox 1.3 44.6 2.1 44.9 --start-date 2006-01-29

This will give you an **overview** of the results (as it's not very convenient to display 20 000 items on a terminal). If you wish to get all the items, you can specify an output json file using :option:`-o, --output` or start working with the programmatic version of |pn|. This output can be loaded as a dataframe later, see :ref:`serialization_of_dataframes`.

.. note::

    To work with dates in the ``search`` CLI, you can use several formats (see availables formats in :py:func:`pygeodes.utils.datetime_utils.complete_datetime_from_str`).

.. _searching_collections:
Searching collections
---------------------

You can also search for collections by adding the parameter :option:`-cs, --collections_search`. It allow only one argument, with is a search term that will be searched in the description and the title of the collections.
For example, to search a collection which is related to the term *grd*, you can do : 

.. code-block:: bash

    pygeodes search -cs "grd"

Downloading items from id
-------------------------

The CLI allows you to download items from their id. For example you could search for an item in the web Geodes_ interface and paste its id here to download it.
To use that feature you need to provide an api key, which can be done by providing a configuration file in json format (see :doc:`configuration`).

.. code-block:: bash

    pygeodes --config config.json download "S1A_IW_SLC__1SSH_20230101T144707_20230101T144722_046591_059567_C90A"

.. _Geodes: https://geodes.cnes.fr

.. _monitoring_downloads:
Monitoring downloads
--------------------

You can monitor all the current and pending downloads on your |pn| instance, using the command ``watch-downloads`` : 

.. code-block:: bash

    pygeodes watch-downloads

Here are the options :

-r RATE, --rate RATE  the refresh rate (in seconds) of the display
-s, --simplified      wether to use the simplified version of the display (may help better rendering on some terminals)

For example :

.. code-block:: bash

    pygeodes watch-downloads -r 1 -s

will display every second in a simplified interface.
