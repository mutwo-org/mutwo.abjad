import itertools
import operator
import typing

from mutwo import core_utilities


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


# Until mutwo.core_utilites has del_nested_item_from_index_sequence,
# we patch it here.
def del_nested_item_from_index_sequence(
    index_sequence: typing.Sequence[int],
    sequence: typing.MutableSequence,
) -> None:
    """Delete item in nested Sequence.

    :param index_sequence: The indices of the nested item which shall be deleted.
    :type index_sequence: typing.Sequence[int]
    :param sequence: A nested sequence.
    :type sequence: typing.MutableSequence[typing.Any]

    **Example:**

    >>> from mutwo import core_utilities
    >>> nested_sequence = [1, 2, [4, [5, 1], [9, [3]]]]
    >>> core_utilities.del_nested_item_from_index_sequence((2, 2, 0), nested_sequence)
    >>> nested_sequence
    [1, 2, [4, [5, 1], [[3]]]]
    """

    index_count = len(index_sequence)
    for index_index, index in enumerate(index_sequence):
        if index_count == index_index + 1:
            sequence.__delitem__(index)
        else:
            sequence = sequence[index]


core_utilities.del_nested_item_from_index_sequence = del_nested_item_from_index_sequence
