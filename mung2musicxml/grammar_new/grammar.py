import re
from typing import Self
from collections import defaultdict

from .parts import (EdgeSignature, GrammarNode, _GrammarDefaultDict, Cardinality,
                    GrammarEdge)
from .symbol import Symbol
from .constants import GrammarConstants
from .violations import GrammarViolation
from .rules import GrammarRule, _RuleSideGroup, _RuleSideGroupType
from .rules.factory import RuleFactory
from .validators import AlphabetValidator, EdgeValidator, CardinalityValidator


class Grammar:
    """
    The DependencyGrammar class implements rules about valid graphs above
    objects from a set of recognized classes.

    The Grammar complements a Parser. It defines rules, and the Parser
    implements algorithms to apply these rules to some input.

    A grammar has an **Alphabet** and **Rules**. The alphabet is a list
    of symbols that the grammar recognizes. Rules are constraints on
    the structures that can be induced among these symbols.

    There are two kinds of grammars according to what kinds of rules
    they use: **dependency** rules, and **constituency** rules. We use
    dependency grammars. Dependency grammar rules specify which symbols
    are governing, and which symbols are governed:

        noteheadFull | stem

    There can be multiple left-hand side and right-hand side symbols,
    as a shortcut for a list of rules:

        noteheadFull | stem beam
        noteheadFull noteheadHalf | legerLine durationDot tie notehead*Small

    The asterisk works as a wildcard. Currently, only one wildcard per symbol
    is allowed:

      timeSignature | numeral*

    Lines starting with a ``#`` are regarded as comments and ignored.
    Empty lines are also ignored.

    **Cardinality rules**

    We can also specify in the grammar the minimum and/or maximum number
    of relationships, both inlinks and outlinks, that an object can form
    with other objects of given types. For example:

    * One notehead may have up to two stems attached.
    * We also allow for stemless full noteheads.
    * One stem can be attached to multiple noteheads, but at least one.

    This would be expressed as:

        notehead*{,2} | stem{1,}

    The relationship of noteheads to leger lines is generally ``m:n``::

        noteheadFull | legerLine

    A time signature may consist of multiple numerals, but only one
    other symbol:

        timeSignature{1,} | numeral*{1}
        timeSignature{1} | timeSigCommon timeSigCutCommon

    A key signature may have any number of sharps and flats.
    A sharp or flat can only belong to one key signature. However,
    not every sharp belongs to a key signature:

        keySignature | accidentalSharp{,1} accidentalFlat{,1} accidentalNatural{,1} accidentalDoubleSharp{,1} accidentalDoubleFlat{,1}

    For the left-hand side of the rule, the cardinality restrictions apply to
    outlinks towards symbols of classes on the right-hand side of the rule.
    For the right-hand side, the cardinality restrictions apply to inlinks
    from symbols of left-hand side classes.

    It is also possible to specify that regardless of where outlinks
    lead, a symbol should always have at least some:

        timeSignature{1,} |
        repeat{2,} |

    And analogously for inlinks:

        | letter*{1,}
        | numeral*{1,}
        | legerLine{1,}
        | noteheadFullSmall{1,}

    **Additions made to the original ``DependencyGrammar``**

    The grammar now checks actual cardinalities - not aggregated ones.
    Make the cardinality rules useful.

    It is possible to use the ``ANYOF()`` token that checks the cardinality
    against the sum of counts of all the symbols inside the brackets.
    For example, we can check if a beam is connected to at least one notehead/rest:

        ANYOF(noteheadFull, noteheadSmall, rest*) | beam{1,}

    This was not possible before, as specifying each rule separately would
    end up demanding the beam to connected to at least one noteheadFull, one noteheadSmall etc.

    It is also now much easier to extend the rules with any other special-non-recursive tokens.
    """
    def __init__(self, rules: list[GrammarRule], alphabet: list[Symbol]):
        self.rules = rules
        self.alphabet = alphabet

        self._alphabet_validator = AlphabetValidator(self.alphabet)
        self._edge_validator = EdgeValidator.from_rules(self.rules)
        self._cardinality_validator = CardinalityValidator(self.rules)

    @classmethod
    def from_text(cls, grammar_text: str, alphabet: list[str] | set[str]) -> Self:
        parser = _GrammarParser(alphabet)
        return parser.parse(grammar_text) # type: ignore
    
    def is_valid_edge_signature(self, edge: EdgeSignature) -> bool:
        return self._edge_validator.is_valid_edge(edge)
    
    def is_valid_edge(self, edge: GrammarEdge) -> bool:
        return self.is_valid_edge_signature(edge.edge_signature)
    
    def is_valid_symbol(self, symbol: Symbol) -> bool:
        return symbol in self.alphabet
    
    @staticmethod
    def _compute_links(edges: list[GrammarEdge]):
        inlinks: defaultdict[GrammarNode, _GrammarDefaultDict[Symbol, list[GrammarNode]]] = defaultdict(lambda: _GrammarDefaultDict(list))
        outlinks: defaultdict[GrammarNode, _GrammarDefaultDict[Symbol, list[GrammarNode]]] = defaultdict(lambda: _GrammarDefaultDict(list))

        for edge in edges:
            source, target = edge.from_node, edge.to_node
            outlinks[source][target.symbol].append(target)
            inlinks[target][source.symbol].append(source)

        return inlinks, outlinks
    
    @staticmethod
    def _to_grammar_nodes(nodes: dict[int, str], edges: set[tuple[int, int]]) -> tuple[list[GrammarNode], list[GrammarEdge]]:
        """
        Transforms simple input data to Grammar's inner representation.
        """
        nodes_ = {id: GrammarNode(Symbol(name), id) for id, name in nodes.items()}
        output_edges = [GrammarEdge(nodes_[from_id], nodes_[to_id]) for from_id, to_id in edges]
        return list(nodes_.values()), output_edges
    
    def find_invalid(self, nodes: dict[int, str], edges: set[tuple[int, int]]) -> list[GrammarViolation]:
        g_nodes, g_edges = self._to_grammar_nodes(nodes, edges)
        
        # Check if names are valid
        name_violations = self._alphabet_validator.find_invalid(g_nodes)
        
        # Check if cardinalities are correct
        inlinks, outlinks = self._compute_links(g_edges)

        link_violations: list[GrammarViolation] = []
        for node in g_nodes:
            inl = inlinks[node]
            outl = outlinks[node]
            link_violations += self._cardinality_validator.find_invalid_inlinks(node, inl)
            link_violations += self._cardinality_validator.find_invalid_outlinks(node, outl)

        # Check if edge signatures are valid
        edge_violations = self._edge_validator.find_invalid(g_edges)

        violations = name_violations + edge_violations + link_violations

        return violations

    def __repr__(self):
        return "\n".join([str(x) for x in self.rules])


class _GrammarParser:
    def __init__(self, alphabet: list[str] | set[str]):
        self._alphabet = alphabet
        self._factory = RuleFactory()


    def parse(self, grammar_text: str) -> Grammar:
        """
        Parses the given text into a ``Grammar`` instance.
        For rule definitions, see the ``Grammar`` class.

        :param grammar_text: Grammar rule definitions.
        :return: Parsed ``Grammar`` instance.
        """
        rules: list[GrammarRule] = []
        for line in grammar_text.splitlines():
            line = line.strip()
            if not line or line.startswith(GrammarConstants.COMMENT_SYMBOL):
                continue
            atomic_rules = self._parse_line_to_rules(line)
            for rule in atomic_rules:
                rules.append(rule)
        return Grammar(rules, [Symbol(x) for x in self._alphabet])
    
    @staticmethod
    def _remove_comment(raw: str) -> str:
        index = raw.find(GrammarConstants.COMMENT_SYMBOL)
        return raw[:index] if index != -1 else raw

    def _parse_line_to_rules(self, line: str) -> list[GrammarRule]:
        if GrammarConstants.RULE_DELIMITER not in line:
            raise ValueError(f"Missing '{GrammarConstants.RULE_DELIMITER}' in rule: {line}")

        parts = line.split(GrammarConstants.RULE_DELIMITER, 1)
        lhs_text, rhs_text = parts[0].strip(), self._remove_comment(parts[1]).strip()

        lhs_groups = self._parse_rule_side_to_groups(lhs_text) if lhs_text else [_RuleSideGroup()]
        rhs_groups = self._parse_rule_side_to_groups(rhs_text) if rhs_text else [_RuleSideGroup()]
        
        rules = []
        for lhs in lhs_groups:
            for rhs in rhs_groups:
                rules += self._factory.create(lhs, rhs)
                    
        return rules
    
    
    def _parse_rule_side_to_groups(self, rule_side: str) -> list[_RuleSideGroup]:
        """
        Parses a single side of rule (left or right) into a list of Groups.
        Group is a list of symbols enclosed in brackets with a token
        or a single class name.

        Example:

            "token(a b c) a b d" -> ["token(a b c)", "a", "b", "c"]
        """
        # Strict match for one group
        group_pattern = re.compile(r'''
            ^                                                   # Start of the group
            (                                                   # --- Main group ---
                (?P<token>\w+)\(                                # TOKEN(
                    (?P<inner>\s*[^\s(){}]+\s*(\s*\s*[^\s(){}]+\s*)*)? # inner: a, b, c with optional spaces
                \)                                              # )
                |
                (?P<class>[^\s(){}]+)                                    # OR: single class name (no spaces inside)
            )
            (?P<cardinality>\{[^\{\}]+\})?                      # Optional cardinality with braces included
            $                                                   # End of the group
        ''', re.VERBOSE)

        def extract_groups(s: str) -> list[str]:
            # Parses the strings into groups,
            # keeps symbols inside brackets together.
            # "token(a b c) a b d" -> ["token(a b c)", "a", "b", "c"]
            groups = []
            buffer = ""
            paren_depth = 0
            brace_depth = 0
            i = 0

            while i < len(s):
                c = s[i]
                if c == "(":
                    if paren_depth == 1:
                        raise ValueError("Nested parentheses are not allowed")
                    paren_depth += 1
                    buffer += c
                elif c == ")":
                    paren_depth -= 1
                    if paren_depth < 0:
                        raise ValueError("Unmatched closing parenthesis")
                    buffer += c
                elif c == "{":
                    brace_depth += 1
                    buffer += c
                elif c == "}":
                    brace_depth -= 1
                    if brace_depth < 0:
                        raise ValueError("Unmatched closing brace")
                    buffer += c
                elif c == " " and paren_depth == 0 and brace_depth == 0:
                    if buffer.strip():
                        groups.append(buffer.strip())
                    buffer = ""
                else:
                    buffer += c
                i += 1

            if buffer.strip():
                groups.append(buffer.strip())
            if paren_depth != 0:
                raise ValueError("Unmatched opening parenthesis")
            if brace_depth != 0:
                raise ValueError("Unmatched opening brace")
            return groups



        raw_groups = extract_groups(rule_side)
        parsed_groups = []

        for raw in raw_groups:
            match = group_pattern.match(raw)
            if not match:
                raise ValueError(f"Invalid group: '{raw}'")

            token = match.group("token")
            inner = match.group("inner")
            class_name = match.group("class")
            cardinality = match.group("cardinality")

            cardinality = Cardinality.from_string(cardinality) if cardinality is not None else Cardinality()

            if token:
                if inner and inner.strip():
                    class_list = [c.strip() for c in inner.split(" ")]
                else:
                    class_list = []
                parsed_groups.append(_RuleSideGroup(
                    type=_RuleSideGroupType.from_str(token),
                    symbols=Symbol.expand_list_of_names_from_alphabet(class_list, self._alphabet),
                    cardinality=cardinality
                    )
                )
            else:
                class_list = Symbol.expand_list_of_names_from_alphabet(class_name.split(" "), self._alphabet)
                for class_name in class_list:
                    parsed_groups.append(_RuleSideGroup(
                        type=_RuleSideGroupType.ATOMIC,
                        symbols=[class_name],
                        cardinality=cardinality
                        )
                    )

        return parsed_groups
