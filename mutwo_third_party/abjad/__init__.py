"""Patch abjad and abjad_converters to fix various bugs"""

__all__ = ("AbjadScoreListToLilyPondFile",)


import abjad


# Monkey patch abjads LeafMaker '_make_tied_leaf`
# in order to allow not-assignable duration and duration
# with numerator > 1 for forbidden_duration
def LeafMaker__make_tied_leaf(
    class_,
    duration,
    increase_monotonic=None,
    forbidden_duration=None,
    multiplier=None,
    pitches=None,
    tag=None,
    tie_parts=True,
):
    duration = abjad.Duration(duration)

    # ###### MONKEY PATCH ##### #
    # if forbidden_duration is not None:
    #     assert forbidden_duration.is_assignable
    #     assert forbidden_duration.numerator == 1
    # ###### MONKEY PATCH ##### #

    # find preferred numerator of written durations if necessary
    if forbidden_duration is not None and forbidden_duration <= duration:
        denominators = [
            2 * forbidden_duration.denominator,
            duration.denominator,
        ]
        denominator = abjad.math.least_common_multiple(*denominators)
        forbidden_duration = abjad.NonreducedFraction(forbidden_duration)
        forbidden_duration = forbidden_duration.with_denominator(denominator)
        duration = abjad.NonreducedFraction(duration)
        duration = duration.with_denominator(denominator)
        forbidden_numerator = forbidden_duration.numerator
        assert forbidden_numerator % 2 == 0
        preferred_numerator = forbidden_numerator / 2
    # make written duration numerators
    numerators = []
    parts = abjad.math.partition_integer_into_canonic_parts(duration.numerator)
    if forbidden_duration is not None and forbidden_duration <= duration:
        for part in parts:
            if forbidden_numerator <= part:
                better_parts = abjad.LeafMaker._partition_less_than_double(
                    part, preferred_numerator
                )
                numerators.extend(better_parts)
            else:
                numerators.append(part)
    else:
        numerators = parts
    # reverse numerators if necessary
    if increase_monotonic:
        numerators = list(reversed(numerators))
    # make one leaf per written duration
    result = []
    for numerator in numerators:
        written_duration = abjad.Duration(numerator, duration.denominator)
        if pitches is not None:
            arguments = (pitches, written_duration)
        else:
            arguments = (written_duration,)
        result.append(class_(*arguments, multiplier=multiplier, tag=tag))
    result = abjad.Selection(result)
    # tie if required
    if tie_parts and 1 < len(result):
        if not issubclass(class_, (abjad.Rest, abjad.Skip)):
            abjad.tie(result)
    return result


abjad.LeafMaker._make_tied_leaf = LeafMaker__make_tied_leaf
