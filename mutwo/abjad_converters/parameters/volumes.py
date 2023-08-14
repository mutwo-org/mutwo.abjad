import typing

from mutwo import abjad_parameters
from mutwo import core_converters
from mutwo import music_parameters

__all__ = ("MutwoVolumeToAbjadAttachmentDynamic",)


class MutwoVolumeToAbjadAttachmentDynamic(core_converters.abc.Converter):
    """Convert Mutwo Volume objects to :class:`~mutwo.abjad_parameters.Dynamic`.

    This default class simply checks if the passed Mutwo object belongs to
    :class:`mutwo.music_parameters.WesternVolume`. If it does, Mutwo
    will initialise the :class:`Tempo` object from the :attr:`name` attribute.
    Otherwise Mutwo will first initialise a :class:`WesternVolume` object via
    its py:method:`mutwo.music_parameters.WesternVolume.from_amplitude` method.

    Hairpins aren't notated with the aid of :class:`mutwo.music_parameters.abc.Volume`
    objects, but with :class:`mutwo.music_parameters.Hairpin`.
    """

    def convert(
        self, volume_to_convert: music_parameters.abc.Volume
    ) -> typing.Optional[abjad_parameters.Dynamic]:
        if not isinstance(volume_to_convert, music_parameters.WesternVolume):
            if volume_to_convert.amplitude > 0:
                volume_to_convert = music_parameters.WesternVolume.from_amplitude(
                    volume_to_convert.amplitude
                )
            else:
                return None
        return abjad_parameters.Dynamic(dynamic_indicator=volume_to_convert.name)
