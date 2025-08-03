"""
This is a working demo of the new implementation of MuNG Grammar.

Run it:

>>> python3 -m mung2musicxml.grammar_new <file_name>
"""

from argparse import ArgumentParser
from pathlib import Path
from mung import NotationGraph
import logging
logging.basicConfig(level=logging.INFO)

from .wrapper import NotationGraphGrammarWrapper


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("file_name", type=Path)
    args = parser.parse_args()

    graph_file: Path = args.file_name
    graph = NotationGraph.from_file(graph_file)

    grammar = NotationGraphGrammarWrapper()

    syntax_violations = grammar.find_invalid_syntax(graph)
    precedence_violations = grammar.find_invalid_precedence(graph)

    print(20*"-")
    print(f"Found {len(syntax_violations)} SYNTAX violations.")
    for v in syntax_violations:
        print(f"> {v}")
    print()

    print(20*"-")
    print(f"Found {len(precedence_violations)} PRECEDENCE violations.")
    for v in precedence_violations:
        print(f"> {v}")