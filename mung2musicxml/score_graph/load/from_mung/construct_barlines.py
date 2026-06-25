from ...graph import LeftRightMiddleToken as LRM, RepeatBarline, Barline
from .construct_barline_mapping import BarStruct, SystemMeasureBarlineHandler
from fractions import Fraction
from collections import defaultdict


def _bar_to_barline_or_repeat(
    bs: BarStruct, limit_onset: Fraction, location: LRM
) -> Barline | RepeatBarline:
    if bs.is_repeat:
        assert bs.bf is not None and bs.wing is not None
        if location != LRM.MIDDLE:
            return RepeatBarline(
                style=bs.style, location=location, bf=bs.bf, winged=bs.wing
            )
        # is on left
        # repeat can be outputted as "middle", but when
        # its onset is zero, it has to be on the left
        elif limit_onset == Fraction(0):
            location = LRM.LEFT
            return RepeatBarline(
                style=bs.style, location=location, bf=bs.bf, winged=bs.wing
            )
        # is truly in the middle
        else:
            return RepeatBarline(
                style=bs.style,
                location=location,
                bf=bs.bf,
                winged=bs.wing,
                fractional_onset_=bs.onset,
            )

    return Barline(bs.style, location)


def _assert_onset(onset: Fraction | None) -> Fraction:
    assert onset is not None
    return onset


def construct_bars_from_bar_mapping(
    bar_mapping: defaultdict[int, defaultdict[int, SystemMeasureBarlineHandler]],
    system_index: int,
    measure_index: int,
    right_barline_onset: Fraction,
) -> list[Barline | RepeatBarline]:
    """
    Retrieves data from barline mapping and constructs
    left, right and middle bars.
    """

    bar_data = bar_mapping[system_index][measure_index]
    left = bar_data.left
    right = bar_data.right

    left = _bar_to_barline_or_repeat(left, Fraction(0), LRM.LEFT)
    right = _bar_to_barline_or_repeat(right, right_barline_onset, LRM.RIGHT)
    middle = [
        _bar_to_barline_or_repeat(bar, _assert_onset(bar.onset), LRM.MIDDLE)
        for bar in bar_data.middle
    ]

    bars = [left, right] + middle

    return bars
