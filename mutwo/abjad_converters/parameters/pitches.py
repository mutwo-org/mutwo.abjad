import abjad  # type: ignore

from mutwo import core_converters
from mutwo import music_parameters

__all__ = ("MutwoPitchToAbjadPitch",)


class MutwoPitchToAbjadPitch(core_converters.abc.Converter):
    """Convert Mutwo Pitch objects to Abjad Pitch objects.

    This default class simply checks if the passed Mutwo object belongs to
    :class:`mutwo.ext.parameters.pitches.WesternPitch`. If it does, Mutwo
    will initialise the Abjad Pitch from the :attr:`name` attribute.
    Otherwise Mutwo will simply initialise the Abjad Pitch from the
    objects :attr:`frequency` attribute.

    If users desire to make more complex conversions (for instance
    due to ``scordatura`` or transpositions of instruments), one can simply
    inherit from this class to define more complex cases.
    """

    def convert(self, pitch_to_convert: music_parameters.abc.Pitch) -> abjad.Pitch:
        if isinstance(pitch_to_convert, music_parameters.WesternPitch):
            return abjad.NamedPitch(pitch_to_convert.name)
        else:
            return abjad.NamedPitch.from_hertz(pitch_to_convert.frequency)
