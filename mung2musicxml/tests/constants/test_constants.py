from unittest import TestCase, main
from parameterized import parameterized

from typing import Optional, Any, Callable
import inspect

from mung.constants import InferenceEngineConstants, ClassNameConstants


def check_list_fields_and_properties(obj: Any, predicate: Callable[[list], bool], skip: Optional[set[str]] = None) -> list[str]:
    if skip is None:
        skip = set()
    bad_fields = []

    def is_bad(value: list) -> bool:
        return isinstance(value, list) and not predicate(value)
    
    # regular class attributes that are lists
    for name, value in vars(obj.__class__).items():
        if name in skip:
            continue
        if is_bad(value):
            bad_fields.append(name)

    # instance attributes that are lists
    for name, value in vars(obj).items():
        if name in skip:
            continue
        if is_bad(value):
            bad_fields.append(name)

    # properties returning lists
    for name, _ in inspect.getmembers(type(obj), lambda m: isinstance(m, property)):
        if name in skip:
            continue
        try:
            value = getattr(obj, name)
        except Exception:
            continue
        if is_bad(value):
            bad_fields.append(name)

    return bad_fields


def predicate_unique(value: list) -> bool:
    assert isinstance(value, list)
    return len(value) == len(set(value))


class TestConstantListFields(TestCase):
    @parameterized.expand(
        [
            (ClassNameConstants.__name__, ClassNameConstants, {}),
            (InferenceEngineConstants.__name__, InferenceEngineConstants, {"PITCH_STEPS"})
        ]
    )
    def test_all_list_members_unique(self, name: str, obj: type, skip: set[str]):
        bad = check_list_fields_and_properties(obj, predicate=lambda lst: len(lst) == len(set(lst)), skip=skip)
        self.assertEqual(bad, [], f"These fields failed the check: {bad}")


if __name__ == "__main__":
    main()