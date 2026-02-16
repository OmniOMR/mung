from unittest import TestCase, main
from parameterized import parameterized

from mung.interpret.time_sig.basic import digits_to_time_signature


class TestDigitParser(TestCase):
    @parameterized.expand([
        # Common cases
        ("common_time_4_4", [4, 4], (4, 4)),
        ("waltz_3_4", [3, 4], (3, 4)),
        ("compound_6_8", [6, 8], (6, 8)),
        ("multi_digit_numerator_12_8", [1, 2, 8], (12, 8)),
        ("large_denominator_5_16", [5, 1, 6], (5, 16)),

        # Edge cases
        ("empty_input", [], None),
        ("single_digit", [4], None),
        ("invalid_denominator", [3, 5], None),
        ("zero_numerator", [0, 4], None),
        ("leading_zero_numerator", [0, 3, 4], None),

        # Preference rule tests
        # Possible splits:
        # 1/24 (valid, not preferred)
        # 12/4 (valid, preferred)
        ("preferred_denominator_wins", [1, 2, 4], (12, 4)),

        # Fallback behavior
        # Possible splits:
        # 7/16 (valid)
        # 71/6 (invalid)
        ("fallback_to_first_valid", [7, 1, 6], (7, 16)),

        # Ambiguous
        # Possible splits:
        # 1/64 (valid)
        # 16/4 (valid, preferred)
        ("complex_ambiguous_prefers_common", [1, 6, 4], (16, 4)),

        # Possible splits:
        # 9/32 (valid)
        # 93/2 (valid, preferred)
        ("preferred_late_split", [9, 3, 2], (93, 2)),
    ])
    def test_advanced_time_signature_parser(self, name, digits, expected):
        self.assertEqual(
            digits_to_time_signature(digits),
            expected
        )


if __name__ == "__main__":
    main()
