# Until mutwo.core_utilites has del_nested_item_from_index_sequence,
# we patch it here.
import typing

from mutwo import core_utilities


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
