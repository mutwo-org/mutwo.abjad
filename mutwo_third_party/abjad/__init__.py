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
    # tie if required
    if tie_parts and 1 < len(result):
        if not issubclass(class_, (abjad.Rest, abjad.Skip)):
            abjad.tie(result)
    return result


# XXX: StringContactPoint was removed in abjad 3.5, see:
#
#       https://github.com/Abjad/abjad/issues/1372
#
# This monkey patch readds it to the abjad namespace.
class _StringContactPoint:
    """
    String contact point.

    ..  container:: example

        Sul ponticello:

        >>> indicator = abjad.StringContactPoint('sul ponticello')
        >>> string = abjad.storage(indicator)
        >>> print(string)
        abjad.StringContactPoint(
            contact_point='sul ponticello',
            )

    ..  container:: example

        Sul tasto:

        >>> indicator = abjad.StringContactPoint('sul tasto')
        >>> string = abjad.storage(indicator)
        >>> print(string)
        abjad.StringContactPoint(
            contact_point='sul tasto',
            )

    """

    ### CLASS VARIABLES ###

    __slots__ = ("_contact_point",)

    _contact_point_abbreviations = {
        "dietro ponticello": "d.p.",
        "molto sul ponticello": "m.s.p",
        "molto sul tasto": "m.s.t.",
        "ordinario": "ord.",
        "pizzicato": "pizz.",
        "ponticello": "p.",
        "sul ponticello": "s.p.",
        "sul tasto": "s.t.",
    }

    _contact_points = (
        "dietro ponticello",
        "molto sul ponticello",
        "molto sul tasto",
        "ordinario",
        "pizzicato",
        "ponticello",
        "sul ponticello",
        "sul tasto",
    )

    _parameter = "SCP"

    _persistent = True

    ### INITIALIZER ###

    def __init__(self, contact_point: str = "ordinario") -> None:
        contact_point = str(contact_point)
        assert contact_point in self._contact_points
        self._contact_point = contact_point

    ### SPECIAL METHODS ###

    def __eq__(self, argument) -> bool:
        """
        Is true when all initialization values of Abjad value object equal
        the initialization values of ``argument``.
        """
        return StorageFormatManager.compare_objects(self, argument)

    def __hash__(self) -> int:
        """
        Hashes Abjad value object.
        """
        hash_values = StorageFormatManager(self).get_hash_values()
        try:
            result = hash(hash_values)
        except TypeError:
            raise TypeError(f"unhashable type: {self}")
        return result

    def __repr__(self) -> str:
        """
        Gets interpreter representation.
        """
        return StorageFormatManager(self).get_repr_format()

    ### PUBLIC PROPERTIES ###

    @property
    def contact_point(self) -> str:
        """
        Gets contact point of string contact point.

        ..  container:: example

            Sul ponticello:

            >>> indicator = abjad.StringContactPoint('sul ponticello')
            >>> indicator.contact_point
            'sul ponticello'

        ..  container:: example

            Sul tasto:

            >>> indicator = abjad.StringContactPoint('sul tasto')
            >>> indicator.contact_point
            'sul tasto'

        Set to known string.
        """
        return self._contact_point

    @property
    def markup_string(self) -> str:
        string = self._contact_point_abbreviations[self.contact_point]
        string = rf"\caps {string.title()}"
        return string

    @property
    def markup(self) -> abjad.Markup:
        r"""
        Gets markup of string contact point.

        ..  container:: example

            Sul ponticello:

            >>> indicator = abjad.StringContactPoint('sul ponticello')
            >>> abjad.show(indicator.markup) # doctest: +SKIP

            ..  docs::

                >>> string = abjad.lilypond(indicator.markup)
                >>> print(string)
                \markup {
                    \caps
                        S.P.
                    }

        ..  container:: example

            Sul tasto:

            >>> indicator = abjad.StringContactPoint('sul tasto')
            >>> abjad.show(indicator.markup) # doctest: +SKIP

            ..  docs::

                >>> string = abjad.lilypond(indicator.markup)
                >>> print(string)
                \markup {
                    \caps
                        S.T.
                    }

        """
        string = rf"^ \markup {{ {self.markup_string} }}"
        markup = abjad.Markup(string)
        return markup

    @property
    def parameter(self) -> str:
        """
        Returns ``'SCP'``.

        ..  container:: example

            >>> abjad.StringContactPoint('sul tasto').parameter
            'SCP'

        """
        return self._parameter

    @property
    def persistent(self) -> bool:
        """
        Is true.

        ..  container:: example

            >>> abjad.StringContactPoint('sul tasto').persistent
            True

        """
        return self._persistent

    @property
    def tweaks(self) -> None:
        """
        Are not implemented on string contact point.
        """
        pass


abjad.LeafMaker._make_tied_leaf = LeafMaker__make_tied_leaf
abjad.StringContactPoint = _StringContactPoint
