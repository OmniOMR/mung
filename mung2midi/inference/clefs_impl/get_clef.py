from typing import Optional
from mung import Node

from ...logger import logger
from .clef_base import ClefBase
from .default_clef import DefaultClef


def get_clef_data_from_node(clef: Optional[Node] = None, permissive: bool = False) -> ClefBase:
    if clef is None:
        logger.warning("Returning default clef, Node is None")
        return DefaultClef()
    
    for sub in ClefBase.__subclasses__():
        if clef.class_name.startswith(sub().name):
            return sub()
    
    if permissive:
        logger.warning(f"Unknown clef name '{clef.class_name}'")
        return DefaultClef()
    else:
        raise ValueError(f"Unknown clef name '{clef.class_name}'")
