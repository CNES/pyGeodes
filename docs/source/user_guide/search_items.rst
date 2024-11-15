Search for items
================

|pn| let's you also search for items, again provided you have a configured :py:class:`pygeodes.geodes.Geodes` object (see :ref:`creating_geodes_object`).

First query
-----------

Then you can start making some queries, let's start by retrieving all items whose orbit direction is **30972** :

.. code-block:: python
    
    query = {"spaceborne:absoluteOrbitID" : {"eq" : 30972}}
    items,dataframe = geodes.search_items(query=query)

.. seealso::

    For more complex queries, see :doc:`building_queries`.

Searching by geometry
---------------------

You can also provide an ``intersects`` parameter, or a ``bbox`` parameter :

.. code-block:: python
    
    geometry = {
            "coordinates": [
            [
                [
                1.0292372559819398,
                44.60770095328709
                ],
                [
                1.2841512336040637,
                44.10175878425329
                ],
                [
                1.9222514382792326,
                45.25223094308308
                ],
                [
                0.7712475295708145,
                45.44578103385132
                ],
                [
                1.0292372559819398,
                44.60770095328709
                ]
            ]
            ],
            "type": "Polygon"
    }

    items,dataframe = geodes.search_items(intersects=geometry)

    # or 

    bbox = [-0.112245,51.552873,-0.104177,51.557143]
    items,dataframe = geodes.search_items(bbox=bbox)

Configuration
-------------

By default, it returns a ``items`` object, which is a list of :py:class:`pygeodes.utils.stac.Item`, and a ``dataframe`` object, which is a ``geopandas.GeoDataframe`` object (please refer to `geopandas docs <https://geopandas.org/en/stable/index.html>`__).

.. seealso::

    For further formatting configuration, see :doc:`manipulating_objects`.

If you wish to get only the items, you can use the parameter ``return_df=False``.

.. code-block:: python
    
    items = geodes.search_items(query=query,return_df=False)

By default, it returns all the objects corresponding to your query, so it can be long (making many API calls) if your query is not really precise. You could just want a little overview of the objects, you can set the parameter ``get_all=False``, to get just the first items returned (by making just one API call).

.. code-block:: python
    
    items = geodes.search_items(query=query,return_df=False,get_all=False)

.. seealso::
    
    You can refer to the implementation of ``search_items`` for further details (:py:meth:`Geodes.search_items`)