# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from __future__ import annotations

import importlib
import inspect
import os
import subprocess
import sys

import sphinx_autosummary_accessors

# Set environment variable to help code determine whether or not we are running a Sphinx doc build process
os.environ["DAFT_SPHINX_BUILD"] = "1"

# Help Sphinx find local custom extensions/directives that we build
sys.path.insert(0, os.path.abspath("ext"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = "Daft API"
copyright = "2025, Eventual"
author = "Eventual"
# html_logo = "_static/daft-logo.png"
html_favicon = "_static/daft-favicon.png"
html_title = "Daft API Documentation"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# The name of a reST role (builtin or Sphinx extension) to use as the default role, that
# is, for text marked up `like this`. This can be set to 'py:obj' to make `filter` a
# cross-reference to the Python function “filter”. The default is None, which doesn’t
# reassign the default role.

default_role = "py:obj"

html_context = {"default_mode": "light"}

extensions = [
    "sphinx_reredirects",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx.ext.linkcode",
    "sphinx.ext.intersphinx",
    "IPython.sphinxext.ipython_console_highlighting",
    "myst_nb",
    "sphinx_copybutton",
    "sphinx_autosummary_accessors",
    "sphinx_tabs.tabs",
    # Local extensions
    "sql_autosummary",
]

templates_path = ["_templates", sphinx_autosummary_accessors.templates_path]

# Removes module names that prefix our classes
add_module_names = False

# -- Options for Notebook rendering
# https://myst-nb.readthedocs.io/en/latest/configuration.html?highlight=nb_execution_mode#execution

nb_execution_mode = "off"


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_css_files = ["header.css", "custom-function-signatures.css"]
html_js_files = ["custom.js"]
html_theme_options = {
    # This is how many levels are shown on the secondary sidebar
    "show_toc_level": 2,
}
# Set canonical link
# Based on Google Search's recommendation, we use an absolute path here. For more details, see:
# https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls#use-rel=canonical-link-annotations
html_baseurl = "https://www.getdaft.io/projects/docs/en/stable/"

# -- Copy button configuration

# This pattern matches:
# - Python Repl prompts (">>> ") and it's continuation ("... ")
# - Bash prompts ("$ ")
# - IPython prompts ("In []: ", "In [999]: ") and it's continuations
#   ("  ...: ", "     : ")
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True


# Resolving code links to github
# Adapted from: https://github.com/aaugustin/websockets/blob/778a1ca6936ac67e7a3fe1bbe585db2eafeaa515/docs/conf.py#L100-L134


commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd="../..").strip().decode("utf-8")
code_url = f"https://github.com/Eventual-Inc/Daft/blob/{commit}"


def linkcode_resolve(domain, info):
    assert domain == "py", "expected only Python objects"
    mod = importlib.import_module(info["module"])
    if "." not in info["fullname"]:
        obj = getattr(mod, info["fullname"])
    elif info["fullname"].count(".") == 1:
        objname, attrname = info["fullname"].split(".")
        obj = getattr(mod, objname)
        try:
            # object is a method of a class
            obj = getattr(obj, attrname)
        except AttributeError:
            # object is an attribute of a class
            return None
    # Accessor methods with 2 "."s
    elif info["fullname"].count(".") == 2:
        objname, accessor_name, method_name = info["fullname"].split(".")
        obj = getattr(getattr(getattr(mod, objname), accessor_name), method_name)

    # Handle case where object is a decorated function
    while hasattr(obj, "__wrapped__"):
        obj = obj.__wrapped__

    try:
        file = inspect.getsourcefile(obj)
        lines = inspect.getsourcelines(obj)
    except (TypeError, OSError):
        # e.g. object is a typing.Union
        return None
    path_start = file.find("daft/")
    if path_start == -1:
        return None
    file = file[path_start:]
    start, end = lines[1], lines[1] + len(lines[0]) - 1

    return f"{code_url}/{file}#L{start}-L{end}"
