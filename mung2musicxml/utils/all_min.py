from typing import TypeVar, Iterable, Callable, Any


T = TypeVar("T")


def all_min(items: Iterable[T], key: Callable[[T], Any] = lambda x: x) -> list[T]:
    items = list(items)
    if not items:
        return []
    min_val = min(key(x) for x in items)
    return [x for x in items if key(x) == min_val]
