from typing import Optional
import numpy as np
from mung import Node


def DummyNode(
    id_: int,
    class_name: str,
    top: int = 0,
    left: int = 0,
    width: int = 0,
    height: int = 0,
    outlinks: Optional[list[int]] = None,
    inlinks: Optional[list[int]] = None,
    mask: Optional[np.ndarray] = None,
    dataset: Optional[str] = None,
    document: Optional[str] = None,
    data=None,
) -> Node:
    return Node(
        id_,
        class_name,
        top,
        left,
        width,
        height,
        outlinks,
        inlinks,
        mask,
        dataset,
        document,
        data,
    )
