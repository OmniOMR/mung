from unittest import TestCase, main
from parameterized import parameterized
from typing import Optional, Any

from mung.constants import ClassNameConstants as C
from mung2musicxml.inference import PitchInferenceEngineWrapper
from ..utils.dummy_staff import _DummyStaffGenerator
from ..utils.tone_generator import next_tones


STAFF_POSITION_COUNT = 11


def transform_names(pitch_names: dict[int, Any]) -> list[Any]:
    return [
        value for _, value
        in sorted(pitch_names.items(), key=lambda x: x[0], reverse=True)
    ]


class ClefShifts(TestCase):
    """
    Test all clefs (C, F, G) with different potential delta shifts.
    Every clef can be snapped to any staffline, but it doesn't have to be.

    These tests go over:

    - Default clef interpretations (without any link to staffline).
    - Clef interpretations when linked to default staffline.
    - Clef interpretations when linked to some staffline.
    """
    generator = _DummyStaffGenerator()
    engine = PitchInferenceEngineWrapper()
        
    @parameterized.expand(
        [
            ("g_clef", C.Clefs.G_CLEF, None, next_tones(("D", 4), STAFF_POSITION_COUNT)),
            ("c_clef", C.Clefs.C_CLEF, None, next_tones(("E", 3), STAFF_POSITION_COUNT)),
            ("f_clef", C.Clefs.F_CLEF, None, next_tones(("F", 2), STAFF_POSITION_COUNT)),
        ]
    )
    def test_clefs_no_snap(
        self, name: str, clef_name: str, clef_delta: Optional[int], expected_tones: list[tuple[str, int]]
    ):
        assert len(expected_tones) == STAFF_POSITION_COUNT
        assert clef_delta is None

        graph = self.generator(clef_name=clef_name, clef_delta=clef_delta)
        names = self.engine(graph)
        
        self.assertListEqual(transform_names(names), expected_tones)
    
    @parameterized.expand(
        [
            ("g_clef", C.Clefs.G_CLEF, 1, next_tones(("D", 4), STAFF_POSITION_COUNT)),
            ("c_clef", C.Clefs.C_CLEF, 2, next_tones(("E", 3), STAFF_POSITION_COUNT)),
            ("f_clef", C.Clefs.F_CLEF, 3, next_tones(("F", 2), STAFF_POSITION_COUNT)),
        ]
    )
    def test_clefs_with_snap_basic(
        self, name: str, clef_name: str, clef_delta: Optional[int], expected_tones: list[tuple[str, int]]
    ):
        assert len(expected_tones) == STAFF_POSITION_COUNT
        assert clef_delta is not None

        graph = self.generator(clef_name=clef_name, clef_delta=clef_delta)
        names = self.engine(graph)
        
        self.assertListEqual(transform_names(names), expected_tones)
    
    @parameterized.expand(
        [
            ("g_clef_delta_0", C.Clefs.G_CLEF, 0, next_tones(("F", 4), STAFF_POSITION_COUNT)),
            ("g_clef_delta_2", C.Clefs.G_CLEF, 2, next_tones(("B", 3), STAFF_POSITION_COUNT)),

            ("c_clef_delta_4", C.Clefs.C_CLEF, 4, next_tones(("A", 2), STAFF_POSITION_COUNT)),
            ("c_clef_delta_3", C.Clefs.C_CLEF, 3, next_tones(("C", 3), STAFF_POSITION_COUNT)),
            ("c_clef_delta_1", C.Clefs.C_CLEF, 1, next_tones(("G", 3), STAFF_POSITION_COUNT)),
            ("c_clef_delta_0", C.Clefs.C_CLEF, 0, next_tones(("B", 3), STAFF_POSITION_COUNT)),

            ("f_clef_delta_2", C.Clefs.F_CLEF, 2, next_tones(("A", 2), STAFF_POSITION_COUNT)),
            ("f_clef_delta_4", C.Clefs.F_CLEF, 4, next_tones(("D", 2), STAFF_POSITION_COUNT)),
        ]
    )
    def test_clefs_with_snap_complex(
        self, name: str, clef_name: str, clef_delta: Optional[int], expected_tones: list[tuple[str, int]]
    ):
        assert len(expected_tones) == STAFF_POSITION_COUNT
        assert clef_delta is not None

        graph = self.generator(clef_name=clef_name, clef_delta=clef_delta)
        names = self.engine(graph)
        
        self.assertListEqual(transform_names(names), expected_tones)
    

if __name__ == "__main__":
    main()