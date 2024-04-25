import typing

import abjad  # type: ignore

try:
    import quicktions as fractions
except ImportError:
    import fractions

from mutwo import core_converters
from mutwo import music_parameters

__all__ = ("MutwoPitchToAbjadPitch",)


class MutwoPitchToAbjadPitch(core_converters.abc.Converter):
    """Convert Mutwo Pitch objects to Abjad Pitch objects.

    :param allowed_division_sequence: :class:`MutwoPitchToAbjadPitch` rounds
        microtonal :class:`music_parameters.WesternPitch` in order to make them
        notatable with Lilypond. By default they are rounded to quarter-tones
        (because Lilypond support quarter-tones). If you'd like to omit quarter
        tones you can set this to ``(fractions.Fraction(1, 1),)``. See also
        the documentation of `round_to` method from
        :class:`music_parameters.WesternPitch` for further information.
    :type allowed_division_sequence: typing.Sequence[fractions.Fraction]

    This default class simply checks if the passed Mutwo object belongs to
    :class:`mutwo.music_parameters.WesternPitch`. If it does, Mutwo
    will initialise the Abjad Pitch from the :attr:`name` attribute.
    Otherwise Mutwo will simply initialise the Abjad Pitch from the
    objects :attr:`hertz` attribute.

    If users desire to make more complex conversions (for instance
    due to ``scordatura`` or transpositions of instruments), one can simply
    inherit from this class to define more complex cases.
    """

    def __init__(
        self,
        allowed_division_sequence: typing.Sequence[fractions.Fraction] = (
            fractions.Fraction(1, 2),
        ),
    ):
        self._allowed_division_sequence = allowed_division_sequence

    def convert(self, pitch_to_convert: music_parameters.abc.Pitch) -> abjad.Pitch:
        if isinstance(pitch_to_convert, music_parameters.WesternPitch):
            return abjad.NamedPitch(
                pitch_to_convert.copy().round_to(
                    self._allowed_division_sequence
                ).name
            )
        else:
            return abjad.NamedPitch.from_hertz(pitch_to_convert.hertz)
