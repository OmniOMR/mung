from pathlib import Path

from ...logger import logger


def _load_grammar_part(data_file_name: str, name: str) -> str:
    local_dir = Path(__file__).parent
    data_file = local_dir / data_file_name
    with open(data_file, "r", encoding="utf8") as f:
        return f.read()
    logger.info(f"Loaded {name} from {data_file}")


PRECEDENCE_GRAMMAR_DEPRULES_TEXT: str = _load_grammar_part("precedence.deprules", "Precedence Deprules")
SYNTAX_GRAMMAR_DEPRULES_TEXT: str = _load_grammar_part("syntax.deprules", "Syntax Deprules")
GRAMMAR_ALPHABET: list[str] = _load_grammar_part("alphabet.txt", "Alphabet").split("\n")
