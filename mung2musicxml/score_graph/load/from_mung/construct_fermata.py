from mung import Node
from ...graph import (
    Fermata,
    FermataOrientationToken,
    Subevent
)


def _match_name_to_orientation(name: str) -> FermataOrientationToken:
    lw = name.lower()
    if lw.endswith("above"):
        return FermataOrientationToken.UPRIGHT
    elif lw.endswith("below"):
        return FermataOrientationToken.INVERTED
    else:
        raise ValueError(f"Unable to match {Fermata.__name__} {name}")


def construct_fermata(mung_fermata: Node, sub: Subevent) -> Fermata:
    return Fermata(sub, _match_name_to_orientation(mung_fermata.class_name))
