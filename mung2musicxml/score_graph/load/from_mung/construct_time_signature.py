from typing import Optional
from mung import Node, NotationGraph
from mung.interpret import (
    TimeSigStruct,
    TimeSignatureInterpreter,
    BasicTimeSignatureInterpreter
)

from ...graph import *


def construct_time_signature(
        mung_time_sig: Node,
        onset: Fraction,
        graph: NotationGraph,
        time_sig_intepreter: Optional[TimeSignatureInterpreter] = None
    ) -> Optional[TimeSignature]:
    if time_sig_intepreter is None:
        time_sig_intepreter = BasicTimeSignatureInterpreter()
    tss = time_sig_intepreter.interpret_time_signature(mung_time_sig, graph)
    
    if tss is None:
        return None
    
    return TimeSignature(
        fractional_onset_=onset,
        numerator=tss.numerator,
        denominator=tss.denominator,
        symbol_type=_get_time_sig_symbol_token(tss),
        separator_type=_get_separator_token(tss)
    )


def _get_time_sig_symbol_token(time_sig: TimeSigStruct) -> TimeSymbolToken:
    if time_sig.is_common:
        return TimeSymbolToken.COMMON
    elif time_sig.is_common_cut:
        return TimeSymbolToken.CUT
    elif time_sig.is_single_number:
        return TimeSymbolToken.SINGLE_NUMBER
    return TimeSymbolToken.NORMAL


def _get_separator_token(time_sig: TimeSigStruct) -> TimeSeparatorToken:
    if time_sig.has_slash:
        return TimeSeparatorToken.HORIZONTAL
    else:
        return TimeSeparatorToken.NONE
    