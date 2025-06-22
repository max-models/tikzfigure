# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import shutil


def copy_tutorials(app):
    src = os.path.abspath("../tutorials")
    dst = os.path.abspath("source/tutorials")

    # Remove existing target directory if it exists
    if os.path.exists(dst):
        shutil.rmtree(dst)

    shutil.copytree(src, dst)


def setup(app):
    app.connect("builder-inited", copy_tutorials)


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "python-template"
copyright = "2025, Max Lindqvist"
author = "Max Lindqvist"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "nbsphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.autodoc",
]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
