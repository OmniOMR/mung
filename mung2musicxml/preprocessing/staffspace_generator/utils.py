from mung import Node
import numpy as np
from typing import Optional

from ..errors import MaskIsNoneError
from ...logger import logger


def _crop_masks_to_horizontal_overlap(
        first_mask: np.ndarray, first_left: int,
        second_mask: np.ndarray, second_left: int,
        first_id: Optional[int] = None, second_id: Optional[int] = None
        ) -> tuple[np.ndarray, np.ndarray]:
    first_right = first_left + first_mask.shape[1]
    second_right = second_left + second_mask.shape[1]

    left_start = max(first_left, second_left)
    right_end = min(first_right, second_right)

    if left_start >= right_end:
        if first_id is not None and second_id is not None:
            logger.warning(f"Given nodes {first_id}, {second_id} do not vertically overlap")
        else:
            logger.warning("Given nodes do not vertically overlap")
        return np.array([], dtype=np.uint8), np.array([], dtype=np.uint8)

    mask1 = first_mask[..., left_start - first_left: first_mask.shape[1] - (first_right - right_end)]
    mask2 = second_mask[..., left_start - second_left: second_mask.shape[1] - (second_right - right_end)]

    return mask1, mask2

def crop_node_masks_to_horizontal_overlap(first: Node, second: Node) -> tuple[np.ndarray, np.ndarray]:
    """
    Returns masks of two given Nodes located in a 2D space
    reduced to their horizontal overlap.

    Example:

    >>> first.mask =  [[0, 0, 0, 0, 1, 1, 1, 1], [1, 1, 1, 1, 0, 0, 0, 0]]
    >>> first.left = 2
    >>> second.mask = [[0, 0, 0, 1, 1, 0], [1, 1, 1, 1, 1, 1], [0, 0, 1, 1, 1, 1]]
    >>> second.right = 5
    >>> crop_node_masks_to_horizontal_overlap(first, second)
    (
        array([[0, 1, 1, 1, 1],
               [1, 0, 0, 0, 0]]),
        array([[0, 0, 0, 1, 1],
               [1, 1, 1, 1, 1],
               [0, 0, 1, 1, 1]])
    )

    """
    if first.mask is None or second.mask is None:
        raise MaskIsNoneError()
    
    return _crop_masks_to_horizontal_overlap(
        first.mask, first.left,
        second.mask, second.left,
        first_id=first.id, second_id=second.id
        )

def interpolate(arr: np.ndarray, wildcard: int = -1) -> np.ndarray:
    """
    Interpolates values inside an array.
    Unknown number is marked with the ``wild_card`` value
    and is filled in based on values around it.

    :param arr: Array to interpolate.
    :param wildcard: Number with which missing values are denoted.
    """
    result = arr.copy()
    known = np.where(arr != wildcard)[0]
    if len(known) == 0:
        return result
    result[:known[0]] = arr[known[0]]
    result[known[-1] + 1:] = arr[known[-1]]
    for i in range(len(known) - 1):
        start, end = known[i], known[i + 1]
        result[start:end + 1] = np.round(np.linspace(arr[start], arr[end], end - start + 1)).astype(int)
    return result


def merge_and_interpolate_top_bottom_masks(
        top_mask: np.ndarray,
        top_y: int,
        bottom_mask: np.ndarray,
        bottom_y: int,
        visualize: bool = False
) -> np.ndarray:
    height_top, width = top_mask.shape
    height_bottom, width2 = bottom_mask.shape

    if width != width2:
        raise ValueError("Masks must have the same width")
    if top_y > bottom_y:
        raise ValueError("Top mask must be higher than bottom mask")

    y_min = min(top_y, bottom_y)
    y_max = max(top_y + height_top, bottom_y + height_bottom)
    total_height = y_max - y_min

    top_offset = top_y - y_min
    bottom_offset = bottom_y - y_min

    top_canvas = np.zeros((total_height, width), dtype=bool)
    bottom_canvas = np.zeros((total_height, width), dtype=bool)
    top_canvas[top_offset:top_offset + height_top] = top_mask
    bottom_canvas[bottom_offset:bottom_offset + height_bottom] = bottom_mask

    # Get first occurrence of 1 (top) and last (bottom) for each column
    top_pos = np.argmax(top_canvas, axis=0)
    no_top = ~np.any(top_canvas, axis=0)
    top_pos[no_top] = -1

    bottom_pos = total_height - 1 - np.argmax(bottom_canvas[::-1], axis=0)
    no_bottom = ~np.any(bottom_canvas, axis=0)
    bottom_pos[no_bottom] = -1

    # Interpolate found values
    top_pos = interpolate(top_pos)
    bottom_pos = interpolate(bottom_pos)

    # Construct output mask with vectorized fill
    rows = np.arange(total_height)[:, None]
    mask: np.ndarray = (rows >= top_pos) & (rows <= bottom_pos)
    mask &= (top_pos != -1) & (bottom_pos != -1)  # ensure valid columns only

    mask = mask.astype(np.uint8)

    if visualize:
        import matplotlib.pyplot as plt

        fig, axs = plt.subplots(3, 1, figsize=(12, 4))
        axs[0].imshow(top_mask, cmap="gray")
        axs[0].set_title("Top Mask")
        axs[1].imshow(bottom_mask, cmap="gray")
        axs[1].set_title("Bottom Mask")
        axs[2].imshow(mask, cmap="gray")
        axs[2].set_title("Merged Mask")

        plt.tight_layout()
        plt.show()

    return mask