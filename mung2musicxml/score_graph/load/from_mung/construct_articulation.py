from mung import Node
from mung.constants import ClassNameConstants as C

from ...graph import *

def construct_articulation(mung_articulation: Node, subevent: Subevent) -> None:
    type_, placement = _mung_class_name_to_articulation_type_and_placement(mung_articulation)
    Articulation(subevent, type_, placement)
    

def _mung_class_name_to_articulation_type_and_placement(articulation: Node) -> tuple[ArticulationType, AboveBelowToken]:
    name = articulation.class_name.lower()
    if name.endswith("above"):
        placement = AboveBelowToken.ABOVE
    elif name.endswith("below"):
        placement = AboveBelowToken.BELOW
    else:
        raise ValueError(f"Articulation name '{articulation.class_name}' does not contain substring 'above' nor 'below'")
    
    clean_name = name[5:-5]
    if clean_name == "marcato":
        type_ = ArticulationType.STRONG_ACCENT
    else:
        type_ = ArticulationType(clean_name)
    
    return type_, placement
