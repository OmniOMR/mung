from unittest import TestCase, main
from parameterized import parameterized

from mung2musicxml.grammar_new.grammar import _GrammarParser
from mung2musicxml.grammar_new.rules import AtomicRule
from mung2musicxml.grammar_new.rules import _RuleSideGroup, _RuleSideGroupType
from mung2musicxml.grammar_new.parts import Cardinality
from mung2musicxml.grammar_new.constants import LinkDirection
from mung2musicxml.grammar_new.symbol import Symbol


class GrammarParserTest(TestCase):
    def setUp(self) -> None:
        self.alphabet = ["a", "b", "c", "d"]
        self.parser = _GrammarParser(self.alphabet)

    @parameterized.expand([
        ("basic", "a | b", Cardinality(), Cardinality(), "a", "b"),
        ("single_value", "a{1} | b{2}", Cardinality(1,1), Cardinality(2,2), "a", "b"),
        ("default_values", "a{,1} | b{2,}", Cardinality(max_links=1), Cardinality(min_links=2), "a", "b"),
    ])
    def test_basic_atomic_rule_parsing(
        self, name: str, input_text: str,
        expected_card_out: Cardinality, expected_card_in: Cardinality,
        expected_s_out: Symbol, expected_s_in: Symbol
        ):
        rules = self.parser.parse(input_text).rules # type: ignore
        assert len(rules) == 2
        assert isinstance(rules[0], AtomicRule) and isinstance(rules[1], AtomicRule)
        assert rules[0].direction != rules[1].direction
        rules: list[AtomicRule]

        # retrieve in/outlink rule
        if rules[0].direction == LinkDirection.OUTLINK:
            out_rule, in_rule = rules[0], rules[1]
        else:
            out_rule, in_rule = rules[1], rules[0]

        self.assertEqual(out_rule.cardinality, expected_card_out)
        self.assertEqual(out_rule.input_class.name, expected_s_out)
        
        self.assertEqual(in_rule.cardinality, expected_card_in)
        self.assertEqual(in_rule.input_class.name, expected_s_in)

    @parameterized.expand([
        ("basic", "a |", LinkDirection.OUTLINK, "a", Cardinality()),
        ("values", "| a{2,9}", LinkDirection.INLINK, "a", Cardinality(2,9)),
    ])
    def test_any_atomic_rule_parsing(
        self, name: str, input_text: str,
        expected_direction: Cardinality, expected_symbol: str,
        expected_card: Cardinality
        ):
        rules = self.parser.parse(input_text).rules
        assert len(rules) == 1
        assert isinstance(rules[0], AtomicRule)
        rule: AtomicRule = rules[0] # type: ignore

        self.assertEqual(rule.direction, expected_direction)
        self.assertEqual(rule.cardinality, expected_card)
        self.assertEqual(rule.input_class.name, expected_symbol)

    @parameterized.expand([
        ("basic", "a b c", [
            _RuleSideGroup(_RuleSideGroupType.ATOMIC, [Symbol("a")], Cardinality()),
            _RuleSideGroup(_RuleSideGroupType.ATOMIC, [Symbol("b")], Cardinality()),
            _RuleSideGroup(_RuleSideGroupType.ATOMIC, [Symbol("c")], Cardinality()),
        ]),
        ("tokenized", "ANYOF(a b)", [
            _RuleSideGroup(_RuleSideGroupType.ANYOF, [Symbol("a"), Symbol("b")], Cardinality()),
        ]),
        ("tokenized_cardinality", "ANYOF(a b){42}", [
            _RuleSideGroup(_RuleSideGroupType.ANYOF, [Symbol("a"), Symbol("b")], Cardinality(42, 42)),
        ]),
        ("tokenized_combined", "a{,1} b{2,3} ANYOF(a b){12,} c EXACTLYONE(d){5}", [
            _RuleSideGroup(_RuleSideGroupType.ATOMIC, [Symbol("a")], Cardinality(max_links=1)),
            _RuleSideGroup(_RuleSideGroupType.ATOMIC, [Symbol("b")], Cardinality(2, 3)),
            _RuleSideGroup(_RuleSideGroupType.ANYOF, [Symbol("a"), Symbol("b")], Cardinality(min_links=12)),
            _RuleSideGroup(_RuleSideGroupType.ATOMIC, [Symbol("c")], Cardinality()),
            _RuleSideGroup(_RuleSideGroupType.EXACTLYONE, [Symbol("d")], Cardinality(5, 5)),
        ]),
    ])
    def test_rule_side(
        self, name: str,
        input_text: str, expected_sequence: list[_RuleSideGroup]
        ):
        groups = self.parser._parse_rule_side_to_groups(input_text)
        self.assertSequenceEqual(groups, expected_sequence)
        


if __name__ == "__main__":
    main()