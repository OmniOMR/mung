from unittest import TestCase, main
from parameterized import parameterized

from mung.constants.utils import AllStrEnumNumeralMapped


def all_subclasses(cls: type) -> set[type]:
    subclasses = set()
    for subclass in cls.__subclasses__():
        subclasses.add(subclass)
        subclasses.update(all_subclasses(subclass))
    return subclasses


class TestConstantLoading(TestCase):
    @parameterized.expand([(sc.__name__, sc) for sc in all_subclasses(AllStrEnumNumeralMapped)])
    def test_number_init(
        self,
        name: str,
        sc: AllStrEnumNumeralMapped
    ):
        try:
            sc._numerals_to_self()
            sc._self_to_numerals()
        except Exception as e:
            self.fail(f"{name} could not create numerals to self or otherwise, {e}")


if __name__ == "__main__":
    main()