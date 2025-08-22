from pathlib import Path

from ...logger import logger


PRECEDENCE_GRAMMAR_DEPRULES_TEXT: str = ""
SYNTAX_GRAMMAR_DEPRULES_TEXT: str = ""
GRAMMAR_ALPHABET: list[str] = []

_data_file = Path(__file__).with_name("precedence.deprules")
with _data_file.open("r", encoding="utf-8") as f:
    PRECEDENCE_GRAMMAR_DEPRULES_TEXT = f.read()
logger.info(f"Loaded Precedence Deprules from {_data_file}")

_data_file = Path(__file__).with_name("syntax.deprules")
with _data_file.open("r", encoding="utf-8") as f:
    SYNTAX_GRAMMAR_DEPRULES_TEXT = f.read()
logger.info(f"Loaded Syntax Deprules from {_data_file}")

_data_file = Path(__file__).with_name("alphabet.txt")
with _data_file.open("r", encoding="utf-8") as f:
    GRAMMAR_ALPHABET = f.read().split("\n")
logger.info(f"Loaded Alphabet from {_data_file}")