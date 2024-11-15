Installation
============

Before installation
-------------------

Before installing, please be sure you use Python 3.10 or upper version, you can test with :bash:`python3 --version`.

**Optional** : you can also create a virtual environment to work (:bash:`python -m venv pygeodes_env && source pygeodes_env/bin/activate`)

Then you're free to either install from PyPi or from source.

From PyPi
-----------------------

You can install |pn| from PyPi by following those steps :

1. Install pygeodes

.. code-block:: bash

    pip install pygeodes

Build from source
-----------------

To build from source, follow those steps : 

1. Clone the repository

.. code-block:: bash

    git clone https://github.com/CNES/pyGeodes

2. Install from source

.. code-block:: bash

    pip install pygeodes/pygeodes

.. tip::

   If you come across an error installing pygeodes with Python 3.11, please refer to :ref:`numpy_error`.