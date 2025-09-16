import numpy as np


def average_index_of_ones_in_column(mask: np.ndarray, col_index: int) -> int:
    """
    Returns the average row index of 1s in a given column of a binary mask.

    :param mask: 2D numpy array of 0s and 1s
    :param col_index: Integer index of the column

    :return: Average row index as float or -1.0 if there are no ones in the column
    """
    if col_index < 0 or col_index >= mask.shape[1]:
        raise IndexError(f"Column index {col_index} is out of bounds for mask with shape {mask.shape}")

    rows_with_ones = np.where(mask[:, col_index] == 1)[0]

    if len(rows_with_ones) == 0:
        return -1

    return int(np.mean(rows_with_ones))