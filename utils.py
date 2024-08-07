from typing import TypeVar, Callable

K = TypeVar("K")
V = TypeVar("V")


def map_indexed(map_func: Callable[[int, K], V], items: list[K]) -> list[V]:
    def inner_map_func(enumerated_item) -> V:
        index = enumerated_item[0]
        value = enumerated_item[1]

        return map_func(index, value)

    return list(map(inner_map_func, enumerate(items)))


def get_subarray(array, start_index, count):
    if start_index < 0:
        raise ValueError("start_index must be non-negative")

    # Ensure start_index doesn't exceed array length
    if start_index >= len(array):
        return []

    # Calculate end_index ensuring it doesn't exceed array length
    safe_end_index = min(start_index + count, len(array))
    return array[start_index:safe_end_index]
