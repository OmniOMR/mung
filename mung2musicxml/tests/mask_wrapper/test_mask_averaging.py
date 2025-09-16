from unittest import TestCase, main
from parameterized import parameterized

import numpy as np
from mung2musicxml.preprocessing.staff_wrapper.mask_wrapper import MaskAverageIndexWrapper


class TestMaskIndexAveraging(TestCase):
    test_mask = np.array(
        [
            #0  1  2  3  4  5  6  7  8  9
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0
            [0, 1, 0, 0, 0, 0, 1, 1, 0, 0],  # 1
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],  # 2
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 3
            [0, 0, 0, 0, 1, 0, 1, 0, 0, 0],  # 4
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],  # 5
        ]
    )
    mask_wrapper = MaskAverageIndexWrapper(test_mask)

    @parameterized.expand(
        [
            # simple
            ("single", 1, 1),
            ("single", 4, 4),
            ("multiple_no_rounding", 7, 3),
            ("multiple_with_rounding", 6, 2),
            # complex
            ("interpolation_normal", 2, 2),
            ("interpolation_normal", 3, 3),
            ("interpolation_with_rounding", 5, 3),
            # edge cases
            ("interpolation_edge_left", 0, 1),
            ("interpolation_edge_right", 8, 3),
            ("interpolation_edge_right", 9, 3),
            ("out_of_bounds_left", -1, 1),
            ("out_of_bounds_right", 100, 3),
        ]
    )
    def test_value_retrieval(self, name: str, index: int, expected: int):
        value = self.mask_wrapper[index]
        self.assertEqual(value, expected)


if __name__ == "__main__":
    main()