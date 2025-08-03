from unittest import TestCase, main

from mung2musicxml.grammar_new.parts import _GrammarDefaultDict
from mung2musicxml.grammar_new.constants import GrammarConstants


class TestGrammarDictionary(TestCase):
    def setUp(self) -> None:
        self.data = _GrammarDefaultDict(list)
        self.data["a"] = [1, 2, 3]
        self.data["b"] = [1, 2]
        self.data["c"] = [4, 5]

    def tearDown(self) -> None:
        self.data.clear()

    def test_single_index(self):
        self.assertCountEqual(self.data["a"], [1, 2, 3])

    def test_group(self):
        self.assertCountEqual(self.data.get_group(["a", "b"]), [1, 2, 3, 1, 2])

    def test_any(self):
        self.assertCountEqual(
            self.data[GrammarConstants.ANY_SYMBOL], [1, 2, 3, 1, 2, 4, 5]
        )


if __name__ == "__main__":
    main()
