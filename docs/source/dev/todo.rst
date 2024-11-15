Todo
====

This page acts as a list of things to be done in the future on |pn| : 

* using some Geodes API endpoint to monitor user download quota and authorize downloads from pygeodes in function
* providing some examples of use of |pn| coupled to rasterio_ or sensorsio_
* providing possibility to run a notebook directly on the JupyterHub to get started faster
* developing a way to serialize started download queues (see :py:class:`pygeodes.utils.profile.DownloadQueue`) to load and complete them later
* linking |pn| to assumerole_ to provide a faster way to use S3 downloading from |pn|
* updating |pn| to solve problems preventing async requests in notebook environment to work
* finding a Query Builder system to facilitate user queries construction (by using maybe JSON schema from the data model in XML format) 
* changing the regex system to find filenames for a glob system (simpler to use)

.. _rasterio: https://rasterio.readthedocs.io/en/stable/
.. _sensorsio: https://github.com/CNES/sensorsio
.. _assumerole: https://gitlab.cnes.fr/hpc/softs/assumerole