# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


from __future__ import annotations

import os
import sys
from datetime import datetime

# Adiciona o diretório src ao caminho de importação do Python.
docs = os.path.abspath(os.path.dirname(__file__))
root = os.path.abspath(os.path.join(docs, ".."))
sys.path.insert(0, os.path.join(root, "src"))


# Informações do projeto.
project = "SME Workflow SDK"
author = "SME São Paulo"
copyright = f"{datetime.now().year}, {author}"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


# Extensões do Sphinx.
extensions: list[str] = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
    "myst_parser",
]

# Tipos de arquivos aceitos pelo Sphinx.
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}


# Idioma da documentação.
language = "pt_BR"

# Configurações do Napoleon (docstrings no padrão Google).
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True

# Configurações do autodoc.
autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
    "member-order": "bysource",
}
autodoc_typehints = "description"
autodoc_typehints_format = "short"


# Evita avisos de referências antecipadas de tipos.
suppress_warnings = [
    "sphinx_autodoc_typehints.forward_reference",
]

# Diretórios e arquivos ignorados.
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output


# Configurações de saída HTML.
html_theme = "sphinx_rtd_theme"
html_baseurl = "https://prefeiturasp.github.io/SME-Workflow-SDK/"
html_static_path = ["_static"]

# Referências externas.
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# Habilita o índice alfabético automático do Sphinx.
html_use_index = True
