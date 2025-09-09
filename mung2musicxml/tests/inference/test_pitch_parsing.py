from unittest import TestCase, main
from parameterized import parameterized

from mung2midi.inference import Pitch, Octave, Alter, Step


class ParseText(TestCase):
    @parameterized.expand(
        [
            ("G0", Pitch(Octave(0), Step("G"), Alter(0))),
            ("A1", Pitch(Octave(1), Step("A"), Alter(0))),
            ("D8", Pitch(Octave(8), Step("D"), Alter(0))),
            ("C9", Pitch(Octave(9), Step("C"), Alter(0))),
        ]
    )
    def test_simple(self, name: str, expected: Pitch):
        self.assertEqual(Pitch.from_string(name), expected)

    @parameterized.expand(
        [
            ("G#0", Pitch(Octave(0), Step("G"), Alter(1))),
            ("Ax1", Pitch(Octave(1), Step("A"), Alter(2))),
            ("Dbb8", Pitch(Octave(8), Step("D"), Alter(-2))),
            ("Cb9", Pitch(Octave(9), Step("C"), Alter(-1))),
        ]
    )
    def test_with_alter(self, name: str, expected: Pitch):
        self.assertEqual(Pitch.from_string(name), expected)

    @parameterized.expand(
        [
            ("A10"),
            ("X2"),
            ("Exx3"),
            ("D"),
        ]
    )
    def test_parse_error(self, name: str):
        with self.assertRaises(ValueError):
            Pitch.from_string(name)


if __name__ == "__main__":
    main()