Downloading
===========

|pn| let's you download items after having searched them.

Prerequisites
-------------

This feature requires you to provide an api key (see :doc:`configuration`).

Once you've got a geodes object (see :ref:`creating_geodes_object`) with you api key in the configuration, you're good to go.

Downloading an item
-------------------

Once you searched for items and find yourself with an ``Item`` object, you can download it by simply doing : 

.. code-block:: python

    geodes.download_item_archive(item) # geodes being your Geodes instance with an api key

This will download the item under its original title in the download directory from your geodes object's configuration (by default the current directory).
But you can also choose a custom filename : 

.. code-block:: python

    geodes.download_item_archive(item,outfile="my_item.zip")

.. note::

    This will still download in the default download directory, use ``./my_item.zip`` if you want to be sure it's in your current working directory.

In a more convenient way, you can also use : 

.. code-block:: python

    item.download_archive()

.. caution::

    Be aware that using ``item.download_archive()`` uses the last created Geodes instance and its conf. So, if you want to control which geodes instance is used, use ``geodes.download_item(item)``

Downloading lots of items
-------------------------

.. important::

    Only works on jupyter notebook environments, for now.

If you find yourself wanting to download lots of items, you could want to monitor/watch your downloads. 
This can be done using a :py:class:`pygeodes.utils.profile.DownloadQueue`. Let's say you have a list of items objects you want to download, you can download them using a queue :

.. code-block:: python

    from pygeodes.utils.profile import DownloadQueue,Profile

    # in a first cell : 

    Profile.reset() # not mandatory but it clears the download history, may help
    items_to_download = [item1,item2,...]

    queue = DownloadQueue(items_to_download,download_dir="/tmp/downloads")

    # in another cell :

    queue.run()

.. note::

    The ``download_dir`` is not mandatory, if you don't provide it, the queue will use the download dir from the conf of the latest Geodes instance created.
    But it's **strongly advised** to provide your own download dir, preferably empty. This helps to avoid pygeodes losing time by constantly checking files and computing checksums in the download directory to check if these files are not the file you're trying to download.

If the queue is interrupted before ending (for example by hitting :kbd:`Ctrl+C`), just re-execute the ``queue.run()`` cell, and it will re-start where it stopped.
While it runs, you can monitor the pending and current downloads (see :ref:`monitoring_downloads`).

When it's finished, you can check if all went well by using : 

.. code-block:: python

    queue.check_integrity()

Downloading from S3
-------------------

If you provided your S3 credentials in your conf, you can use `boto3 <https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration>`__ to download items directly from the datalake.
Provided your conf contains your S3 credentials (see :doc:`configuration`), any use of ``geodes.download_item_archive`` or ``item.download_archive`` will use the S3 client instead of geodes.
If you wish to use the s3 client for other purpose (exploring buckets for example), you can use the S3 client this way : 

.. code-block:: python

    for bucket in geodes.s3_client.buckets.all(): # s3_client is already configured with your credentials
        print(bucket.name)