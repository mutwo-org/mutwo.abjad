import itertools
import operator


__all__ = ("group_consecutive_numbers",)


def group_consecutive_numbers(number_tuple: tuple[int, ...]) -> list[list[int]]:
    """Group consecutive numbers into the lists

    **Example**:

    >>> from mutwo import abjad_utilities
    >>> abjad_utilities.group_consecutive_numbers([1,2,4,5, 10, 15, 16])
    [[1, 2], [4, 5], [10], [15, 16]]
    """
    d = []
    for k, g in itertools.groupby(enumerate(number_tuple), lambda t: t[1] - t[0]):
        d.append(list(map(operator.itemgetter(1), g)))
    return d
