Search for collections
======================

|pn| let's you search for collections, provided you have a configured :py:class:`pygeodes.geodes.Geodes` object (see :ref:`creating_geodes_object`).

First query
-----------

Then you can start making some queries, let's start by retrieving all collections who are related to the term *grd* :

.. code-block:: python
    
    collections,dataframe = geodes.search_collections("grd")

But you can also provide a query in JSON format : 

.. code-block:: python
    
    query = {'title' : {'contains' : 'PEPS'}}
    collections,dataframe = geodes.search_collections(query=query)

.. seealso::

    For more complex queries, see :doc:`building_queries`.

Configuration
-------------

By default, it returns a ``collections`` object, which is a list of :py:class:`pygeodes.utils.stac.Collection`, and a ``dataframe`` object, which is a ``geopandas.GeoDataframe`` object (please refer to `geopandas docs <https://geopandas.org/en/stable/index.html>`__).

.. seealso::

    For further formatting configuration, see :doc:`manipulating_objects`.

If you wish to get only the collections, you can use the parameter ``return_df=False``.

.. code-block:: python
    
    collections = geodes.search_collections(query=query,return_df=False)

.. seealso::
    
    You can refer to the implementation of ``search_collections`` for further details (:py:meth:`Geodes.search_collections`)