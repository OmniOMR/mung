from unittest import TestCase, main
from parameterized import parameterized
import numpy as np
import numpy.testing as npt

from mung2musicxml.preprocessing.staffspace_generator.utils import interpolate, merge_and_interpolate_top_bottom_masks


class InterpolationTest(TestCase):
    @parameterized.expand(
        [
            ("basic", np.array([1, 1, 1, 1, 1, 1]), np.array([1, 1, 1, 1, 1, 1])),
            (
                "basic_missing_single",
                np.array([1, 1, 1, -1, 1, 1]),
                np.array([1, 1, 1, 1, 1, 1]),
            ),
            (
                "basic_missing_single_left",
                np.array([-1, 1, 1, 1, 1, 1]),
                np.array([1, 1, 1, 1, 1, 1]),
            ),
            (
                "basic_missing_single_right",
                np.array([1, 1, 1, 1, 1, -1]),
                np.array([1, 1, 1, 1, 1, 1]),
            ),
            (
                "basic_missing_multiple_left",
                np.array([-1, -1, -1, 1, 1, 1]),
                np.array([1, 1, 1, 1, 1, 1]),
            ),
            (
                "basic_missing_multiple_right",
                np.array([1, 1, 1, -1, -1, -1]),
                np.array([1, 1, 1, 1, 1, 1]),
            ),
            (
                "complex_missing_single",
                np.array([1, -1, 3, 4, 5, 6]),
                np.array([1, 2, 3, 4, 5, 6]),
            ),
            (
                "complex_missing_multiple",
                np.array([1, -1, -1, -1, -1, 6]),
                np.array([1, 2, 3, 4, 5, 6]),
            ),
            (
                "complex_missing_multiple",
                np.array([5, 2, -1, -1, 5, 9, -1, 6, 5, -1]),
                np.array([5, 2, 3, 4, 5, 9, 8, 6, 5, 5]),
            ),
        ]
    )
    def test_interpolate(
        self, name: str, input_arr: np.ndarray, expected_arr: np.ndarray
    ):
        interpolated_arr = interpolate(input_arr)
        npt.assert_array_equal(interpolated_arr, expected_arr)


class MergeTest(TestCase):
    @parameterized.expand(
        [
            (
                "basic",
                np.array(
                    [
                        [1, 1, 1, 1, 0, 0, 0, 0],
                        [0, 0, 0, 0, 1, 1, 1, 1],
                    ]
                ),
                2,
                np.array(
                    [
                        [1, 1, 1, 1, 0, 0, 0, 0],
                        [0, 0, 0, 0, 1, 1, 1, 1],
                    ]
                ),
                3,
                np.array(
                    [
                        [1, 1, 1, 1, 0, 0, 0, 0],
                        [1, 1, 1, 1, 1, 1, 1, 1],
                        [0, 0, 0, 0, 1, 1, 1, 1],
                    ]
                ),
            ),
            (
                "interpolation",
                np.array(
                    [
                        [1, 0, 0, 1, 0, 0, 0, 0],
                        [0, 0, 0, 0, 1, 1, 1, 0],
                    ]
                ),
                2,
                np.array(
                    [
                        [1, 0, 0, 1, 0, 0, 0, 0],
                        [0, 0, 0, 0, 1, 0, 1, 1],
                    ]
                ),
                3,
                np.array(
                    [
                        [1, 1, 1, 1, 0, 0, 0, 0],
                        [1, 1, 1, 1, 1, 1, 1, 1],
                        [0, 0, 0, 0, 1, 1, 1, 1],
                    ]
                ),
            ),
            (
                "multiple_values_in_one_column",
                np.array(
                    [
                        [1, 1, 0, 1, 0, 0, 0, 0],
                        [0, 1, 0, 0, 1, 1, 1, 0],
                        [1, 1, 0, 1, 1, 1, 0, 0],
                    ]
                ),
                2,
                np.array(
                    [
                        [1, 0, 0, 1, 0, 0, 0, 0],
                        [0, 0, 0, 0, 1, 0, 1, 1],
                    ]
                ),
                3,
                np.array(
                    [
                        [1, 1, 1, 1, 0, 0, 0, 0],
                        [1, 1, 1, 1, 1, 1, 1, 1],
                        [0, 0, 0, 0, 1, 1, 1, 1],
                    ]
                ),
            )
        ]
    )
    def test_mask_merge(
        self,
        name: str,
        top_mask: np.ndarray,
        top_y: int,
        bottom_mask: np.ndarray,
        bottom_y: int,
        expected_mask: np.ndarray,
    ):
        merged_mask = merge_and_interpolate_top_bottom_masks(top_mask, top_y, bottom_mask, bottom_y)
        npt.assert_array_equal(merged_mask, expected_mask)


if __name__ == "__main__":
    main()
