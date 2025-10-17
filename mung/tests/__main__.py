"""
Equivalent of:

>>> python -m unittest discover . -p test_*.py

if called like this:

>>> python -m mung.tests

Supports additional argument passing, example:

>>> python -m mung.tests -v
"""
from unittest import main
import sys
from pathlib import Path


if __name__ == "__main__":
    assert __package__ is not None
    start_dir = __package__.split(".")[0]
    main(
        module=None,
        argv=["", "discover", "-s", start_dir, "-p", "test_*.py"] + sys.argv[1:]
    )