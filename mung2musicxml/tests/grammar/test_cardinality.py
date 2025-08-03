from unittest import TestCase, main
from parameterized import parameterized

from mung2musicxml.grammar_new.parts import Cardinality
from mung2musicxml.grammar_new.constants import GrammarConstants


class TestCardinality(TestCase):
    @parameterized.expand(
        [
            ("basic", "{0,1}", 0, 1),
            ("basic", "{12,85}", 12, 85),
            ("only_left", "{5,}", 5, GrammarConstants.DEFAULT_UPPER_LIMIT),
            ("only_right", "{,23}", GrammarConstants.DEFAULT_LOWER_LIMIT, 23),
            ("single", "{6}", 6, 6),
        ]
    )
    def test_parse_cases(
        self, name: str, input_text: str, expected_min: int, expected_max: int
    ):
        c = Cardinality.from_string(input_text)
        self.assertEqual(c.min, expected_min)
        self.assertEqual(c.max, expected_max)
    
    @parameterized.expand(
        [
            ("parenthesis_only", "{}"),
            ("parenthesis_incorrect", "{{1,2}"),
            ("parenthesis_incorrect", "1,2"),
            ("empty", "{,}"),
            ("non_numbers", "{a,b}"),
            ("many_numbers", "{1,2,3}"),
            ("min_greater_than_max", "{2,1}"),
        ]
    )
    def test_parse_error(self, name: str, input_text: str):
        with self.assertRaises(ValueError):
            Cardinality.from_string(input_text)


if __name__ == "__main__":
    main()
