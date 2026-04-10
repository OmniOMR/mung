from mung.constants import (
    ClassNameConstants as C,
    InferenceEngineConstants as I
)
from mung import Node, NotationGraph

from ...graph import *
from ....logger import logger

def construct_accidental_for_notehead(notehead: Node, note: Note | GraceNote, graph: NotationGraph) -> None:
    accidentals = graph.children(notehead, class_filter=I.ACCIDENTAL_CLASS_NAMES)
    if len(accidentals) == 0:
        return
    
    names = [a.class_name for a in accidentals]
    # no need to return, the accidental is linked automatically
    Accidental(
        type_=_acc_type_from_multiple_mung_class_names(names),
        parent=note
    )

def construct_accidental_for_key(accidental: Node, key: Key) -> None:
    Accidental(
            type_=_acc_type_from_mung_class_name(accidental.class_name),
            parent=key,
        )


def _acc_type_from_mung_class_name(class_name: str) -> AccidentalValue:
    _LOOKUP = {
        C.Accidentals.ACCIDENTAL_DOUBLE_FLAT : AccidentalValue.FLAT_FLAT,
        C.Accidentals.ACCIDENTAL_FLAT : AccidentalValue.FLAT,
        C.Accidentals.ACCIDENTAL_NATURAL : AccidentalValue.NATURAL,
        C.Accidentals.ACCIDENTAL_SHARP : AccidentalValue.SHARP,
        C.Accidentals.ACCIDENTAL_DOUBLE_SHARP : AccidentalValue.DOUBLE_SHARP
    }
    output = _LOOKUP.get(class_name) # type: ignore
    if output is None:
        raise ValueError(f"Unknown accidental type '{class_name}'")
    return output


def _acc_type_from_multiple_mung_class_names(names: list[str]) -> AccidentalValue:
    if len(names) == 2:
        try:
            return _acc_type_from_two_mung_class_names(names[0], names[1])
        except Exception as e:
            logger.warning(e)
            logger.warning(f"Trying first given name only, '{names[0]}'")

    if len(names) > 2:
        logger.warning(f"Trying first given name only, '{names[0]}'")
    
    return _acc_type_from_mung_class_name(names[0])


def _acc_type_from_two_mung_class_names(class_name1: str, class_name2: str) -> AccidentalValue:
    if class_name1 == class_name2:
        match class_name1:
            case C.Accidentals.ACCIDENTAL_FLAT:
                return AccidentalValue.FLAT_FLAT
            case C.Accidentals.ACCIDENTAL_SHARP:
                return AccidentalValue.SHARP_SHARP
            case _:
                raise ValueError(f"Cannot deduce name from given class names: "
                                    f"'{class_name1}', '{class_name2}'")
    
    match set([class_name1, class_name2]):
        case set([C.Accidentals.ACCIDENTAL_NATURAL, C.Accidentals.ACCIDENTAL_FLAT]):
            return AccidentalValue.NATURAL_FLAT
        case set([C.Accidentals.ACCIDENTAL_NATURAL, C.Accidentals.ACCIDENTAL_SHARP]):
            return AccidentalValue.NATURAL_SHARP
        case _:
            raise ValueError(f"Cannot deduce name from given class names: "
                                f"'{class_name1}', '{class_name2}'")


