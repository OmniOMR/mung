from unittest import TestCase, main
from parameterized import parameterized
from typing import Any

from mung2midi.inference import PitchInferenceEngine, Pitch
from ..utils.dummy_staff import _DummyStaffGenerator


def sort_pitches(pitches: dict[int, Any]) -> list[Any]:
    return [
        value for _, value
        in sorted(pitches.items(), key=lambda x: x[0], reverse=True)
    ]


class KeySignatureShifts(TestCase):
    """
    Tests some standard key signatures.
    """
    generator = _DummyStaffGenerator()
    engine = PitchInferenceEngine()

    @parameterized.expand(
        [
            ("g_major", 1, Pitch.from_list_of_strings(["D4", "E4", "F#4", "G4", "A4", "B4", "C5", "D5", "E5", "F#5", "G5"])),
            ("eb_major", -3, Pitch.from_list_of_strings(["D4", "Eb4", "F4", "G4", "Ab4", "Bb4", "C5", "D5", "Eb5", "F5", "G5"])),
            ("b_major", 5, Pitch.from_list_of_strings(["D#4", "E4", "F#4", "G#4", "A#4", "B4", "C#5", "D#5", "E5", "F#5", "G#5"])),
        ]
    )
    def test_dummy(self, name: str, key_signature: int, expected: list[Pitch]):
        g = self.generator(key_signature=key_signature)
        _, pitches = self.engine.infer_pitches(g.vertices, with_pitch_objects=True)
        pitches = sort_pitches(pitches)
        
        self.assertListEqual(pitches, expected)


if __name__ == "__main__":
    main()