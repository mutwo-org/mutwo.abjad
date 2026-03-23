from mutwo import core_converters
from mutwo import music_parameters


__all__ = ("MutwoLyricToAbjadString",)


class MutwoLyricToAbjadString(core_converters.abc.Converter):
    def convert(self, mutwo_lyric_to_convert: music_parameters.abc.Lyric) -> str:
        if text := mutwo_lyric_to_convert.text:
            if mutwo_lyric_to_convert.ties_next:
                text = f"{text} --"
            return text
        else:
            return "_"
