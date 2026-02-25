from fractions import Fraction
from mung import Node
from mung.constants import OnsetDataConstants as O
from ....inference import PitchDataConstants as P
from ....preprocessing.voices.engine import VoiceDataConstants as V
from ...graph import Pitch, Note, Durable


def duration_beats(durable: Node) -> Fraction:
    return durable.data[O.DURATION_BEATS]


def duration_beats_w_m(durable: Node) -> Fraction:
    return durable.data[O.DURATION_BEATS_WO_M]


def onset_beats(durable: Node) -> Fraction:
    return durable.data[O.ONSET_BEATS]


def pitch(durable: Node) -> Pitch:
    return durable.data[P.PITCH]


def voice(durable: Node) -> int:
    return durable.data[V.VOICE_ID]


def tuple_time_modification(tuplet: Node) -> Fraction:
    return tuplet.data[O.TUPLE_TIME_MODIFICATION]


def get_durable_pitch(durable: Durable) -> int:
    """
    Returns the durable pitch as midi `int`,
    `-1` if the durable does not have a pitch.
    """
    if isinstance(durable, Note):
        return durable.pitch.to_midi()
    return -1
