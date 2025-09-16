from mung.constants import InferenceEngineConstants, ClassNamesConstants

from .base import SnapEngineBase


class RestSnapEngine(SnapEngineBase):
    _SYMBOL_NAMES = InferenceEngineConstants().REST_CLASS_NAMES


class RepeatOneBarSnapEngine(SnapEngineBase):
    _SYMBOL_NAMES = ClassNamesConstants.REPEAT_ONE_BAR


class TimeSignatureSnapEngine(SnapEngineBase):
    _SYMBOL_NAMES = InferenceEngineConstants.TIME_SIGNATURES


class KeySignatureSnapEngine(SnapEngineBase):
    _SYMBOL_NAMES = ClassNamesConstants.KEY_SIGNATURE


class ClefSnapEngine(SnapEngineBase):
    _SYMBOL_NAMES = InferenceEngineConstants().CLEF_CLASS_NAMES
