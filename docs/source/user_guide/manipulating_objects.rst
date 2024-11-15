Manipulating objects
====================

This capter aims to guide you in the all the objects you can find in |pn|.

Working with STAC objects
-------------------------

With STAC objects (:py:class:`pygeodes.utils.stac.Item` and :py:class:`pygeodes.utils.stac.Collection`), you can get the info using method ``find`` associated to the name of a column.

.. _working_with_dataframes:
Working with dataframes
-----------------------

A way to work in |pn| is to work with ``geopandas.GeoDataFrame``, which can get from an items research or from a list of STAC objects.

From STAC objects to dataframes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To create you first dataframe from STAC objects, you can use :py:func:`pygeodes.utils.formatting.format_collections` and :py:func:`pygeodes.utils.formatting.format_items`.
For example from a list of :py:class:`pygeodes.utils.stac.Item`, if I want to create a dataframe and add the column ``spaceborne:cloudCover`` : 

.. code-block:: python

    from pygeodes.utils.formatting import format_items
    items = [item1,item2,...]
    
    dataframe = format_items(items,columns_to_add={"spaceborne:cloudCover"})

But if I put a dataframe instead of a list of items in ``format_items``, the columns will be added to the ones already in the dataframe.

.. hint::

    To explore the available columns you can build dataframes with, use method ``list_available_keys`` on an ``Item`` or a ``Collection`` object.

Filtering in the dataframes
^^^^^^^^^^^^^^^^^^^^^^^^^^^

After having added the columns you want, you can filter your data using the dataframes, let's say we want a cloud cover inferior to 10%.

.. code-block:: python
    
    dataframe = format_items(items,columns_to_add={"spaceborne:cloudCover"})
    filtered = dataframe[dataframe["spaceborne:cloudCover"] <= 10]

.. seealso::

    To explore dataframe filtering options, see pandas docs_ on the subject.

.. _docs: https://pandas.pydata.org/docs/user_guide/indexing.html#boolean-indexing

From dataframes to STAC objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once we filtered our dataframe of items, we could want to download them, so we need to get back our items objects.

.. code-block:: python
    
    items = filtered['item'].values # with 'filtered' being any items dataframe
    for item in items:
        item.download_archive()

.. _serialization_of_dataframes:
Serialization of dataframes
^^^^^^^^^^^^^^^^^^^^^^^^^^^

You could want to serialize a dataframe to work with it later, it's possible using :py:func:`pygeodes.utils.formatting.export_dataframe`

.. code-block:: python
    
    from pygeodes.utils.formatting import export_dataframe

    export_dataframe(dataframe,"df.json")

and you can load it later using :py:func:`pygeodes.utils.formatting.load_dataframe` : 

.. code-block:: python
    
    from pygeodes.utils.formatting import export_dataframe

    dataframe = load_dataframe("df.json")

Plotting and exploring data using dataframes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can see where your data is located on a map using ``dataframe.explore`` : 

.. code-block:: python
    
    dataframe.explore()

.. note::

    The default EPSG_ used to plot is ``4326``, but you can change it, see `geopandas docs <https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.explore.html#geopandas.GeoDataFrame.explore>`__. 

.. _EPSG: https://en.wikipedia.org/wiki/EPSG_Geodetic_Parameter_Dataset

For more examples on using dataframes to explore your data and plot, see :doc:`/examples/dataframes-example`.