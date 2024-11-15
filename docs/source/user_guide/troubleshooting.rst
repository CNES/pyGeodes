Troubleshooting
===============

This section aims to answer questions that you could ask yourself or solve bugs or unexpected behaviours that you could come across.

Buggy display while using ``watch-downloads``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you find yourself with a buggy table using :bash:`pygeodes watch-downloads` or :py:meth:`profile.Profile.watch_downloads`, please test using the parameter ``-s, --simplified`` (see :ref:`monitoring_downloads`) or the parameter ``simplified`` in case of using the function.

Little latency between downloads
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you perform successive downloads and you observe a little latency time between downloads, it might be caused by |pn| crawling files in the download directory to see if the file you're trying to download is not already downloaded somewhere in the directory, which can be long.
To avoid that behaviour, use a fresh new empty download dir.

*'Exceeded 30 redirects'*
^^^^^^^^^^^^^^^^^^^^^^^^^

If you find yourself stuck with an error of type *'Exceeded 30 redirects'*, it's probably because your api key is outdated or false.

.. _numpy_error:
*'numpy.dtype size changed, may indicate binary incompatibility. Expected 96 from C header, got 88 from PyObject'*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You might come accross this error while using pygeodes (in particular if you use Python 3.11). To solve this problem, downgrade your ``numpy`` version by using :

.. code-block:: bash

    python3 -m pip install numpy==1.26.4
    
This should close the issue.