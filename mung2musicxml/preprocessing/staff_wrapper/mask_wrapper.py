import numpy as np


class MaskAverageIndexWrapper:
    def __init__(self, mask: np.ndarray):
        if not self.is_binary_2d_array(mask):
            raise ValueError("Unsupported mask type")
        
        self._height, self._width = mask.shape
        self._mask = mask.astype(np.uint8)

    def __getitem__(self, index: int) -> int:
        """
        Returns the average 1s row index in given column.

        If the given index is outside of the bounds of the mask,
        returns the closest value inside the mask.

        Indexing with ``-1`` results in a computation at index ``0`` -
        the closest index that is in bounds.
        """
        if index < 0:
            return self.average_row_index_of_ones_with_neighbors(0)
        if index >= self._width:
            return self.average_row_index_of_ones_with_neighbors(self._width - 1)
        return self.average_row_index_of_ones_with_neighbors(index)
    
    @staticmethod
    def is_binary_2d_array(arr: np.ndarray) -> bool:
        return (
            isinstance(arr, np.ndarray)
            and arr.ndim == 2
            and bool(np.isin(arr, [0, 1]).all())
        )
    
    def average_row_index_of_ones_with_neighbors(self, col_idx: int) -> int:
        """
        Return the average row index of 1s in the given column of a binary 2D numpy array.
        If the column has no 1s, look left and right until 1s are found.
        If both directions have 1s, average them weighted by distance.
        If only one direction has 1s (edge is hit on the other one), use that side.
        If no 1s exist at all, raise an error, illegal mask.
        """
        # helper to get mean row index of 1s in a column
        def mean_in_col(c: int):
            rows = np.where(self._mask[:, c] == 1)[0]
            return rows.mean() if rows.size > 0 else None

        # check target column first
        base_mean = mean_in_col(col_idx)
        if base_mean is not None:
            return int(base_mean)

        left_mean = None
        right_mean = None
        left_index = right_index = None #type: ignore

        # search left
        for index in range(col_idx - 1, 0 - 1, -1):
            val = mean_in_col(index)
            if val is not None:
                left_mean = val
                left_index = index
                break

        # search right
        for index in range(col_idx + 1, self._width):
            val = mean_in_col(index)
            if val is not None:
                right_mean = val
                right_index = index
                break
        
        # combine results
        if left_mean is not None and right_mean is not None:
            right_index: int
            left_index: int
            return int(left_mean + (right_mean - left_mean) * (col_idx - left_index) / (right_index - left_index))
        elif left_mean is not None:
            return int(left_mean)
        elif right_mean is not None:
            return int(right_mean)
        else:
            raise ValueError("Mask full of zeros is illegal")
