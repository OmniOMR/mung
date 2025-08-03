import fnmatch
from dataclasses import dataclass
from typing import Self, Any


@dataclass(frozen=True, eq=True)
class Symbol:
    name: str

    WILDCARD_TOKEN = "*"

    @staticmethod
    def is_wildcard(raw: str) -> bool:
        return Symbol.WILDCARD_TOKEN in raw

    @classmethod
    def expand_name_from_alphabet(
        cls, raw: str, alphabet: list[str] | set[str]
    ) -> list[Self]:
        if Symbol.is_wildcard(raw):
            matches = fnmatch.filter(alphabet, raw)
            if not matches:
                raise ValueError(
                    f'No matches for wildcard pattern "{raw}" in alphabet.'
                )
            return [cls(name=match) for match in matches]
        else:
            return [cls(name=raw)]

    @classmethod
    def expand_list_of_names_from_alphabet(
        cls, raws: list[str], alphabet: list[str] | set[str]
    ) -> list[Self]:
        output = []
        for raw in raws:
            output += cls.expand_name_from_alphabet(raw, alphabet)
        return output

    def __repr__(self):
        return self.name

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Symbol) and self.name == other.name
