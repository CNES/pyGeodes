Documentation
=============

The documentation is built using Sphinx_.

.. _Sphinx: https://www.sphinx-doc.org/en/master/


Add new static pages
--------------------

The static pages you can add are written in reStructuredText (.rst). 
You need to put them in the ``docs/source`` folder with a ``.rst`` extension.

For example, this page looks like this in reStructuredText : 

.. code-block:: text

    Documentation
    =============

    The documentation is built using Sphinx_.

    .. _Sphinx: https://www.sphinx-doc.org/en/master/


    Add new static pages
    --------------------

    The static pages you can add are written in reStructuredText (.rst). 
    You need to put them in the ``docs/source`` folder with a ``.rst`` extension.

    For example, this page looks like this in reStructuredText : 

    .. code-block:: text

        Documentation
        =============

        The documentation is built using Sphinx_.

        .. _Sphinx: https://www.sphinx-doc.org/en/master/


        Add new static pages
        --------------------

        The static pages you can add are written in reStructuredText (.rst). 
        You need to put them in the ``docs/source`` folder with a ``.rst`` extension.

        For example, this page looks like this in reStructuredText : 

        .. code-block:: text

            # nothing there, otherwise we have an infinite recursion

        .. seealso::

        For further details about the *reStructuredText* syntax, see the Sphinx docs_
        
        .. _docs: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#rst-primer

        

    .. seealso::

    For further details about the *reStructuredText* syntax, see the Sphinx docs_
    
    .. _docs: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#rst-primer

    

.. seealso::

   For further details about the *reStructuredText* syntax, see the Sphinx docs_
   
   .. _docs: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#rst-primer

Add docs to the code
--------------------

The documented code can be interpreted in HTML to give nice API docs, for examples, see  :py:mod:`pygeodes`.

To properly document a function, you need to respect the *numpydoc* convention, let's see an example function : 

.. include:: file_exists.rst

To see the result given in HTML, please see :py:func:`pygeodes.utils.io.file_exists`.

When you write a new function/class, just add your docs using the *numpydoc* syntax. When using ``make build_docs`` command (see :doc:`makefile`), changes will be reflected in the HTML docs.

.. seealso::

   For further details about *numpydoc*, see the numpydoc syntax manual_
   
   .. _manual: https://numpydoc.readthedocs.io/en/latest/install.html

Configuration
-------------

Sphinx can be configured using the ``docs/source/conf.py`` file.
At the end of this file, we define variables that can used everywhere in the ``.rst`` files in the docs.

.. seealso::
    
    For complete documentation about the Sphinx ``conf.py``, see this page_

    .. _page: https://www.sphinx-doc.org/en/master/usage/configuration.html
