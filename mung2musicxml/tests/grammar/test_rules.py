from unittest import TestCase, main
from parameterized import parameterized

from mung2musicxml.grammar_new.rules import AnyOfRule, ExactlyOneRule, AtomicRule, GrammarRule
from mung2musicxml.grammar_new import Grammar
from mung2musicxml.grammar_new.parts import Cardinality
from mung2musicxml.grammar_new.symbol import Symbol
from mung2musicxml.grammar_new.constants import LinkDirection


class RuleEvaluationTest(TestCase):
    def setUp(self):
        self.alphabet = ["a", "b", "c"]
        self.grammar_base = "a b c | a b c"
        self.nodes: dict[int, str] = {
            0: "a",
            1: "a",
            2: "b",
            3: "b",
            4: "c",
            5: "c",
            6: "c",
        }
        self.edges: set[tuple[int, int]] = {
            (0, 2),
            (0, 3),
            (2, 0),
            (2, 1),
            (2, 4),
            (4, 0),
            (4, 1),
            (5, 1),
            (5, 2)
        }

    def tearDown(self):
        self.alphabet.clear()
        self.nodes.clear()
        self.edges.clear()

    @parameterized.expand([
        ("basic", "a | b", 0),
        ("basic", "a{1} | b", 2),
        ("basic", "a{,1} | b", 1),
    ])
    def test_atomic(self, name: str, rule: str, expected_err_count: int):
        # Allow all basic edges + tested rule, we test cardinalities, not edge existence
        grammar = Grammar.from_text(self.grammar_base + "\n" + rule, self.alphabet)

        violations = grammar.find_invalid(self.nodes, self.edges)
        
        self.assertEqual(len(violations), expected_err_count)
    
    @parameterized.expand([
        ("basic", "b | ANYOF(a c)", 0),
        ("basic", "b{1,} | ANYOF(a c)", 1),
        ("basic", "b{2,} | ANYOF(a c)", 1),
        ("basic", "b{3,} | ANYOF(a c)", 1),
        ("basic", "b{4,} | ANYOF(a c)", 2),
    ])
    def test_anyof(self, name: str, rule: str, expected_err_count: int):
        # Allow all basic edges + tested rule, we test cardinalities, not edge existence
        grammar = Grammar.from_text(self.grammar_base + "\n" + rule, self.alphabet)

        violations = grammar.find_invalid(self.nodes, self.edges)
                
        self.assertEqual(len(violations), expected_err_count)

    @parameterized.expand([
        ("basic", "c | EXACTLYONE(a b)", 1),
        ("basic", "c{1,} | EXACTLYONE(a b)", 2),
        ("basic", "c{2,} | EXACTLYONE(a b)", 2),
    ])
    def test_exactlyone(self, name: str, rule: str, expected_err_count: int):
        # Allow all basic edges + tested rule, we test cardinalities, not edge existence
        grammar = Grammar.from_text(self.grammar_base + "\n" + rule, self.alphabet)

        violations = grammar.find_invalid(self.nodes, self.edges)
        
        self.assertEqual(len(violations), expected_err_count)


if __name__ == "__main__":
    main()