import abjad

__all__ = ("concatenate_adjacent_tuplets",)


def concatenate_adjacent_tuplets(voice: abjad.Voice):
    """Rewrite tuplets in voice, so that adjacent tuplets are concatenated if possible.

    :param voice: The voice which should be rewritten. This :class:`abjad.Voice`
        should contain bars (e.g. :class:`abjad.Container`) with leaves or tuplets.
    :type voice: abjad.Voice
    """
    for bar in voice:
        _concatenate_adjacent_tuplets_for_one_bar(bar)


def _concatenate_adjacent_tuplets_for_one_bar(bar: abjad.Container):
    tuplet_index_tuple = _find_tuplet_indices(bar)
    if tuplet_index_tuple:
        grouped_tuplet_index_list_list = _group_tuplet_indices(tuplet_index_tuple)
        for tuplet_index_list in reversed(grouped_tuplet_index_list_list):
            if len(tuplet_index_list) > 1:
                _concatenate_adjacent_tuplets_for_one_group(bar, tuplet_index_list)


def _find_tuplet_indices(bar: abjad.Container) -> tuple[int, ...]:
    tuplet_index_list = []
    for index, leaf_or_tuplet in enumerate(bar):
        if isinstance(leaf_or_tuplet, abjad.Tuplet):
            tuplet_index_list.append(index)

    return tuple(tuplet_index_list)


def _group_tuplet_indices(tuplet_index_tuple: tuple[int, ...]) -> list[list[int]]:
    """Put adjacent tuplet indices into groups."""

    grouped_tuplet_index_list = [[]]
    last_tuplet_index = None
    for tuplet_index in tuplet_index_tuple:
        if last_tuplet_index:
            difference = tuplet_index - last_tuplet_index
            if difference == 1:
                grouped_tuplet_index_list[-1].append(tuplet_index)
            else:
                grouped_tuplet_index_list.append([tuplet_index])
        else:
            grouped_tuplet_index_list[-1].append(tuplet_index)
        last_tuplet_index = tuplet_index
    return grouped_tuplet_index_list


def _concatenate_adjacent_tuplets_for_one_group(bar: abjad.Container, group: list[int]):
    implied_prolation_list = [bar[index].implied_prolation for index in group]
    common_prolation_group_list = [[implied_prolation_list[0], [group[0]]]]
    for index, prolation in zip(group[1:], implied_prolation_list[1:]):
        if prolation == common_prolation_group_list[-1][0]:
            common_prolation_group_list[-1][1].append(index)
        else:
            common_prolation_group_list.append([prolation, [index]])

    tuplet_list = []
    for prolation, tuplet_index_list in common_prolation_group_list:
        tuplet = abjad.Tuplet(prolation)
        for tuplet_index in tuplet_index_list:
            for component in bar[tuplet_index]:
                tuplet.append(abjad.mutate.copy(component))
        tuplet_list.append(tuplet)

    bar[group[0] : group[-1] + 1] = tuplet_list
