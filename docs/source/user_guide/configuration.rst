Configuration
=============

Configuration
-------------

To start using |pn|, you need to configure it. 
It can be done by several ways :

From the default filename
^^^^^^^^^^^^^^^^^^^^^^^^^

You can also use the default filename, |default_config_filename| :

.. code-block:: python

    from pygeodes import Config
    
    conf = Config.from_file() # works only if the default filename is in your cwd

From a specified file 
^^^^^^^^^^^^^^^^^^^^^

|pn| let's you also specify a file from which to load your config : 

.. code-block:: python

    from pygeodes import Config
    
    conf = Config.from_file("path/to/my/conf-file.json")

Manually
^^^^^^^^

You can also specify manually all the config parameters in the :py:class:`pygeodes.utils.config.Config` class : 

.. code-block:: python

    from pygeodes import Config
    
    conf = Config(api_key="myApiKey",logging_level="DEBUG")
    
.. _config_parameters:
Config parameters
^^^^^^^^^^^^^^^^^

Here is a list of all the config parameters that you can use : 


.. list-table::
    :widths: auto
    :header-rows: 1

    *   - name
        - type
        - default
        - description
    *   - ``api_key``
        - :keyword:`str`
        - 
        - Your geodes api key (to learn how to get one, see `geodes docs <https://geodes.cnes.fr/api/#toc6>`__)
    *   - ``logging_level``
        - ``["DEBUG","INFO"]``
        - |default_logging_level|
        - The logging level you want to have, DEBUG is more verbose than INFO
    *   - ``download_dir``
        - :keyword:`str`
        - 
        - The default directory in which your file downloads will be placed
    *   - ``checksum_error``
        - :keyword:`bool`
        - :keyword:`True`
        - Wether to raise an error if the checksum of your file is different from the server checksum
    *   - ``use_async_requests``
        - :keyword:`bool`
        - :keyword:`True`
        - Wether to use async requests in geodes (doesn't work in notebook environments)
    *   - ``aws_access_key_id``
        - :keyword:`str`
        - 
        - See `boto3 configuration <https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration>`__
    *   - ``aws_secret_access_key``
        - :keyword:`str`
        - 
        - See `boto3 configuration <https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration>`__
    *   - ``aws_session_token``
        - :keyword:`str`
        - 
        - See `boto3 configuration <https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration>`__
    *   - ``region_name``
        - :keyword:`str`
        - ``"us-east-1"``
        - See `boto3 configuration <https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration>`__

Here's an example of what your configuration could look like (it's a minimal example) : 

.. code-block:: json

    {"api_key" : "myApiKey","logging_level" : "DEBUG","download_dir" : "/tmp"}

.. _creating_geodes_object:
Creating your ``Geodes`` object
-------------------------------
    
When you have your :py:class:`pygeodes.utils.config.Config` ready, you can start working with geodes :


.. code-block:: python

    from pygeodes import Geodes
    
    geodes = Geodes(conf=conf)

Then you can start working around by searching for some collections, see :doc:`search_collections`.

