"""
This module contains validators that can be run on a simple general graph.

For validators, that are designed to work with MuNG ``NotationGraph``,
see the ``mung_validators`` module.
"""
from .alphabet import AlphabetValidator
from .cardinality import CardinalityValidator
from .edge import EdgeValidator