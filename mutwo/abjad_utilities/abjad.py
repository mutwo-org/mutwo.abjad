try:
    import quicktions as fractions
except ImportError:
    import fractions

import abjad

from mutwo import abjad_utilities

__all__ = ("concatenate_adjacent_tuplets", "reduce_multiplier")


def reduce_multiplier(voice: abjad.Voice):
    """Reduces multipliers of tuplets in ``voice``.

    Essentially the same as :func:`rmakers.reduce_multiplier`, see:
        https://github.com/Abjad/abjad-ext-rmakers/blob/ebb47f6/abjadext/rmakers/functions.py#L3781
    """
    for t in abjad.select.tuplets(voice):
        fraction = abjad.Fraction(t.multiplier.numerator, t.multiplier.denominator)
        pair = fraction.numerator, fraction.denominator
        t.multiplier = pair


def concatenate_adjacent_tuplets(voice: abjad.Voice):
    """Rewrite tuplets in voice, so that adjacent tuplets are concatenated if possible.

    :param voice: The voice which should be rewritten. This :class:`abjad.Voice`
        should contain bars (e.g. :class:`abjad.Container`) with leaves or tuplets.
    :type voice: abjad.Voice
    """
    [_concatenate_adjacent_tuplets(bar) for bar in voice]


def _concatenate_adjacent_tuplets(bar: abjad.Container):
    """Concatenate adjacent tuplets in one bar"""
    tuplet_index_tuple = tuple(
        i for i, e in enumerate(bar) if isinstance(e, abjad.Tuplet)
    )
    g = abjad_utilities.group_consecutive_numbers(tuplet_index_tuple)
    for tuplet_index_list in reversed(g):
        _concatenate_adjacent_tuplets_for_one_group(bar, tuplet_index_list)


def _concatenate_adjacent_tuplets_for_one_group(bar: abjad.Container, group: list[int]):
    if len(group) < 2:  # We can't concatenate 1 element
        return

    prolation_list = [bar[i].implied_prolation for i in group]
    # We now sort our tuplets by their prolation: if two or more
    # consecutive tuplets have the same prolation, they are put into
    # the same group.
    common_prolation_group_list = [[prolation_list[0], [group[0]]]]
    any_common = False
    for i, prolation in zip(group[1:], prolation_list[1:]):
        if prolation == common_prolation_group_list[-1][0]:
            common_prolation_group_list[-1][1].append(i)
            any_common = True
        else:
            common_prolation_group_list.append([prolation, [i]])

    # Only do expensive copy and inplace mutation if there is any
    # group of consecutive tuplets which can be concatenated.
    if not any_common:
        return

    tuplet_list = []
    for prolation, tuplet_index_list in common_prolation_group_list:
        t = abjad.Tuplet(prolation)
        for i in tuplet_index_list:
            for component in bar[i]:
                t.append(abjad.mutate.copy(component))
        tuplet_list.append(t)

    bar[group[0] : group[-1] + 1] = tuplet_list
