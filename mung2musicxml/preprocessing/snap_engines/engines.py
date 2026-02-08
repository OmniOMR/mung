from mung.constants import InferenceEngineConstants  as I, ClassNameConstants as C

from .base import SnapEngineBase


class RestSnapEngine(SnapEngineBase):
    _SYMBOL_NAMES = I.REST_CLASS_NAMES


class RepeatOneBarSnapEngine(SnapEngineBase):
    _SYMBOL_NAMES = C.Repeat.REPEAT_1_BAR


class TimeSignatureSnapEngine(SnapEngineBase):
    _SYMBOL_NAMES = I.TIME_SIGNATURES


class KeySignatureSnapEngine(SnapEngineBase):
    _SYMBOL_NAMES = C.KeySignature.KEY_SIGNATURE


class ClefSnapEngine(SnapEngineBase):
    _SYMBOL_NAMES = I.CLEF_CLASS_NAMES
