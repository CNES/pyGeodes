# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from pathlib import Path
import sys
import os

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

extensions = [
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.autosummary",
    "numpydoc",
    "sphinx_copybutton",
    "nbsphinx",
    "IPython.sphinxext.ipython_console_highlighting",
    "jupyter_sphinx",
]

autosummary_generate = True

templates_path = ["_templates"]
exclude_patterns = ["**.ipynb_checkpoints"]

from pygeodes._info import version, name, description, author

project = name
copyright = "2024, CNES 2024"
release = version
gitlab = "https://gitlab.cnes.fr/pygeodes/pygeodes"

html_title = f"{project} v{release} Manual"

html_theme_options = {
    "gitlab_url": gitlab,
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "external_links": [
        {"name": "Geodes", "url": "https://geodes.cnes.fr"},
    ],
    "collapse_navigation": True,
    "show_prev_next": True,
    "footer_start": ["copyright"],
    "footer_end": [],
    "logo": {
        "image_light": "_static/logo-geodes-light.png",
        "image_dark": "_static/logo-geodes-dark.png",
    },
}


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_css_files = [
    "css/custom.css",
]

html_show_sourcelink = False

import inspect
from pygeodes.utils.io import file_exists
from pygeodes.utils.consts import CONFIG_DEFAULT_FILENAME, DEFAULT_LOGGING_LEVEL

# this code adds the current implementation of pygeodes.utils.io.file_exists to be included as example in the document dev/docs.rst

content = f".. code-block:: python\n\n\t{inspect.getsource(file_exists)}"

with open(
    Path(__file__).resolve().parent.joinpath("dev").joinpath("file_exists.rst"),
    "w",
) as file:
    file.write(content)

rst_epilog = """
.. role:: bash(code)
   :language: bash\n

.. |pn| replace:: {project_name}\n
.. |gl| replace:: {gitlab}\n
.. |default_config_filename| replace:: {default_config_filename}\n
.. |default_logging_level| replace:: ``"{default_logging_level}"``\n
""".format(
    project_name=project,
    gitlab=gitlab,
    default_config_filename=CONFIG_DEFAULT_FILENAME,
    default_logging_level=DEFAULT_LOGGING_LEVEL,
)
