# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("../src"))

# Copy tutorial notebooks from project root to docs/source/tutorials/
tutorials_source = Path(__file__).parent.parent / "tutorials"
tutorials_dest = Path(__file__).parent / "tutorials"

if tutorials_source.exists():
    tutorials_dest.mkdir(exist_ok=True)
    for notebook in tutorials_source.glob("*.ipynb"):
        shutil.copy2(notebook, tutorials_dest / notebook.name)


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "tikzpics"
copyright = "2025, Max"
author = "Max"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinxcontrib.mermaid",
    "sphinx_design",
    "nbsphinx",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**/.ipynb_checkpoints"]

# nbsphinx configuration
nbsphinx_execute = "always"  # Execute notebooks during build


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_book_theme"

html_theme_options = {
    "repository_branch": "devel",
    "show_toc_level": 2,
    "secondary_sidebar_items": ["page-toc"],
    "use_sidenotes": True,
    "home_page_in_toc": True,
    "collapse_navigation": False,
    "navigation_depth": 2,
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/max-models/tikzpics/",
            "icon": "fab fa-github",
            "type": "fontawesome",
        },
        {
            "name": "⭐ Star us!",
            "url": "https://github.com/max-models/tikzpics/",
            "icon": "fas fa-star",
            "type": "fontawesome",
        },
    ],
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
breathe_separate_member_pages = False
html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

autosummary_generate = True

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}
