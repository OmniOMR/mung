from .impl import AnyOfRule, AtomicRule, ExactlyOneRule
from .base import GrammarRule
from .side_group import _RuleSideGroup, _RuleSideGroupType
from ..constants import LinkDirection, GrammarConstants


class RuleFactory(object):
    def _raise_unsupported_combination(self):
        raise ValueError("Unsupported RuleType combination.")
    
    def create(self, lhs: _RuleSideGroup, rhs: _RuleSideGroup) -> list[GrammarRule]:
        if lhs.type == _RuleSideGroupType.ATOMIC and rhs.type == _RuleSideGroupType.ATOMIC:
            return self._rules_from_atomic_groups(lhs, rhs)
        elif ((lhs.type == _RuleSideGroupType.ATOMIC and rhs.type == _RuleSideGroupType.ANYOF)
                or (rhs.type == _RuleSideGroupType.ATOMIC and lhs.type == _RuleSideGroupType.ANYOF)):
            return self._rules_from_any_of(lhs, rhs)
        elif ((lhs.type == _RuleSideGroupType.ATOMIC and rhs.type == _RuleSideGroupType.EXACTLYONE)
                or (rhs.type == _RuleSideGroupType.ATOMIC and lhs.type == _RuleSideGroupType.EXACTLYONE)):
            return self._rules_from_exactly_one(lhs, rhs)
        
        self._raise_unsupported_combination()
        
        
    def _rules_from_atomic_groups(self, lhs: _RuleSideGroup, rhs:_RuleSideGroup) -> list[GrammarRule]:
        assert lhs.type == _RuleSideGroupType.ATOMIC and rhs.type == _RuleSideGroupType.ATOMIC

        rules = []
        lhs_symbol, rhs_symbol = lhs.symbols[0], rhs.symbols[0]

        if lhs.symbols == rhs.symbols == GrammarConstants.ANY_SYMBOL:
            raise ValueError("Cannot have 'ANY' on both sides of an Atomic Rule. "
                             f"This might be caused by an empty rule, such as only '{GrammarConstants.RULE_DELIMITER}'.")
        
        # Cannot directly check for "ANY" symbol in a given graph,
        # omit the rule if it comes from "ANY"
        if lhs_symbol != GrammarConstants.ANY_SYMBOL:
            rules.append(AtomicRule(
                input_class=lhs_symbol,
                output_class=rhs_symbol,
                cardinality=lhs.cardinality,
                direction=LinkDirection.OUTLINK
            ))
        if rhs_symbol != GrammarConstants.ANY_SYMBOL:
            rules.append(AtomicRule(
                input_class=rhs_symbol,
                output_class=lhs_symbol,
                cardinality=rhs.cardinality,
                direction=LinkDirection.INLINK
            ))
        
        return rules

    def _rules_from_any_of(self, lhs: _RuleSideGroup, rhs: _RuleSideGroup) -> list[GrammarRule]:
        rules = []

        if (lhs.type == _RuleSideGroupType.ATOMIC and rhs.type == _RuleSideGroupType.ANYOF):
            rules.append(AnyOfRule(
                input_class=lhs.symbols[0],
                output_classes=rhs.symbols,
                cardinality=lhs.cardinality,
                direction=LinkDirection.OUTLINK
            ))
            for rhs_symbol in rhs.symbols:
                rules.append(AtomicRule(
                    input_class=rhs_symbol,
                    output_class=lhs.symbols[0],
                    cardinality=rhs.cardinality,
                    direction=LinkDirection.INLINK
                )
            )
            
            return rules
        elif (rhs.type == _RuleSideGroupType.ATOMIC and lhs.type == _RuleSideGroupType.ANYOF):
            rules.append(AnyOfRule(
                input_class=rhs.symbols[0],
                output_classes=lhs.symbols,
                cardinality=rhs.cardinality,
                direction=LinkDirection.INLINK
            ))
            for lhs_symbol in lhs.symbols:
                rules.append(AtomicRule(
                    input_class=lhs_symbol,
                    output_class=rhs.symbols[0],
                    cardinality=lhs.cardinality,
                    direction=LinkDirection.OUTLINK
                ))
            
            return rules

        self._raise_unsupported_combination()

    
    def _rules_from_exactly_one(self, lhs: _RuleSideGroup, rhs: _RuleSideGroup) -> list[GrammarRule]:
        rules = []

        if (lhs.type == _RuleSideGroupType.ATOMIC and rhs.type == _RuleSideGroupType.EXACTLYONE):
            rules.append(ExactlyOneRule(
                input_class=lhs.symbols[0],
                output_classes=rhs.symbols,
                cardinality=lhs.cardinality,
                direction=LinkDirection.OUTLINK
            ))
            for rhs_symbol in rhs.symbols:
                rules.append(AtomicRule(
                    input_class=rhs_symbol,
                    output_class=lhs.symbols[0],
                    cardinality=rhs.cardinality,
                    direction=LinkDirection.INLINK
                )
            )
            
            return rules
        elif (rhs.type == _RuleSideGroupType.ATOMIC and lhs.type == _RuleSideGroupType.EXACTLYONE):
            rules.append(ExactlyOneRule(
                input_class=rhs.symbols[0],
                output_classes=lhs.symbols,
                cardinality=rhs.cardinality,
                direction=LinkDirection.INLINK
            ))
            for lhs_symbol in lhs.symbols:
                rules.append(AtomicRule(
                    input_class=lhs_symbol,
                    output_class=rhs.symbols[0],
                    cardinality=lhs.cardinality,
                    direction=LinkDirection.OUTLINK
                ))
            
            return rules
        
        self._raise_unsupported_combination()
