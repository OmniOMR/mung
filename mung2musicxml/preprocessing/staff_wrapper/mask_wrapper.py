import numpy as np


class MaskAverageIndexWrapper:
    def __init__(self, mask: np.ndarray):
        if not self.is_binary_2d_array(mask):
            raise ValueError("Unsupported mask type")
        self.__mask = mask.astype(np.uint8)
        self.__counts = self.average_index_of_ones_in_columns(mask)

    def __getitem__(self, index: int) -> int:
        if index < 0:
            return self.__counts[0]
        if index >= self.__counts.shape[0]:
            return self.__counts[-1]
        return self.__counts[index]

    @staticmethod
    def is_binary_2d_array(arr: np.ndarray) -> bool:
        return (
            isinstance(arr, np.ndarray)
            and arr.ndim == 2
            and bool(np.isin(arr, [0, 1]).all())
        )
    
    @staticmethod
    def average_index_of_ones_in_columns(mask: np.ndarray) -> np.ndarray:
        assert MaskAverageIndexWrapper.is_binary_2d_array(mask)

        rows, _ = mask.shape
        row_indices = np.arange(rows)[:, ...].reshape(-1, 1)
        # Count of 1s per column
        counts = mask.sum(axis=0)
        
        # Sum of indices where 1s are
        weighted = mask * row_indices
        sums = weighted.sum(axis=0)

        # Avoid division by zero -- set result to -1 where count is 0
        with np.errstate(divide="ignore", invalid="ignore"):
            averages = sums / counts
            averages[counts == 0] = -1
            averages: np.ndarray
        
        return averages.astype(int)
            
