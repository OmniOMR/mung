"""
Equivalent of:

>>> python -m unittest discover . -p test_*.py

if called like this:

>>> python -m mung2musicxml.tests

Supports additional argument passing, example:

>>> python -m mung2musicxml.tests -v
"""
from unittest import main
import sys


if __name__ == "__main__":
    main(
        module=None,
        argv=["", "discover", "-p", "test_*.py"] + sys.argv[1:]
    )