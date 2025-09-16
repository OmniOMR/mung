from unittest import TestCase, main
import numpy as np
import numpy.testing as npt

from mung2musicxml.preprocessing.staffspace_generator.utils import _crop_masks_to_horizontal_overlap


class CropTest(TestCase):
    def test_crop_0(self):
        first = np.array([
            [0, 0, 0, 0, 0, 1, 1],
            [0, 0, 1, 1, 1, 0, 0],
            [1, 1, 0, 0, 0, 0, 0],
        ], dtype=np.uint8)
        second = first.copy()

        new_first, new_second = _crop_masks_to_horizontal_overlap(first, 2, second, 0)

        expected_first = np.array([
            [0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1],
            [1, 1, 0, 0, 0],
        ], dtype=np.uint8)
        expected_second = np.array([
            [0, 0, 0, 1, 1],
            [1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0],
        ], dtype=np.uint8)

        npt.assert_array_equal(new_first, expected_first)
        npt.assert_array_equal(new_second, expected_second)

    def test_crop_1(self):
        first = np.array([
            [0, 0, 0, 0, 0, 1, 1, 1],
            [0, 0, 1, 1, 1, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0],
        ], dtype=np.uint8)
        second = np.array([
            [0, 0, 0, 0, 0, 1, 1],
            [0, 0, 1, 1, 1, 0, 0],
            [1, 1, 0, 0, 0, 0, 0],
        ], dtype=np.uint8)

        new_first, new_second = _crop_masks_to_horizontal_overlap(first, 3, second, 1)

        expected_first = np.array([
            [0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1],
            [0, 1, 0, 0, 0],
            [1, 0, 0, 0, 0],
        ], dtype=np.uint8)
        expected_second = np.array([
            [0, 0, 0, 1, 1],
            [1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0],
        ], dtype=np.uint8)

        npt.assert_array_equal(new_first, expected_first)
        npt.assert_array_equal(new_second, expected_second)


if __name__ == "__main__":
    main()
