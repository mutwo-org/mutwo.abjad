from mutwo import core_converters
from mutwo import music_parameters


__all__ = ("MutwoLyricToAbjadString",)


class MutwoLyricToAbjadString(core_converters.abc.Converter):
    def convert(self, mutwo_lyric_to_convert: music_parameters.abc.Lyric) -> str:
        written_representation = mutwo_lyric_to_convert.written_representation
        if written_representation:
            if (
                hasattr(mutwo_lyric_to_convert, "is_last_syllable")
                and not mutwo_lyric_to_convert.is_last_syllable
            ):
                written_representation = f"{written_representation} --"
            return written_representation
        else:
            return "_"
