import difflib
import functools
import os
import typing
import unittest

import abjad

from mutwo import core_events
from mutwo import music_events


__all__ = ("AbjadTestCase", "run_if_ekmelily_available")


class AbjadTestCase(unittest.TestCase):
    base_path = f"tests{os.sep}testdata"

    @staticmethod
    def t(reset_tests: bool = False, force_png: bool = False):
        def t(test_method: typing.Callable):
            return lambda self: self._test(
                test_method.__name__,
                reset_tests,
                force_png=force_png,
                **test_method(self),
            )

        return t

    def setUp(self):
        header_block = abjad.Block(name="header")
        header_block.items.append('tagline = "---integration-test---"')
        self.lilypond_file = abjad.LilyPondFile()
        self.score_block = abjad.Block(name="score")
        self.lilypond_file.items.append(
            "\n".join(
                (
                    r'\include "lilypond-book-preamble.ly"',
                    r"#(ly:set-option 'tall-page-formats 'png)",
                )
            )
        )
        self.lilypond_file.items.extend([header_block, self.score_block])

    def _test(
        self,
        name: str,
        reset_tests: bool = False,
        force_png: bool = False,
        converter=None,
        ev: core_events.abc.Event = core_events.Consecution(
            [core_events.Chronon(1)]
        ),
    ):
        if converter is None:
            converter = self._abjad_converters.ConsecutionToAbjadVoice()

        converted_event = converter.convert(_parse_event(ev))

        p = self.base_path

        ly_ok_path = f"{p}{os.sep}{name}_ok.ly"
        ly_test_path = f"{p}{os.sep}{name}_test.ly"

        png_ok_path = f"{p}{os.sep}{name}_ok.png"
        png_test_path = f"{p}{os.sep}{name}_test.png"

        match converted_event:
            case abjad.Voice():
                item = abjad.Staff([converted_event])
            case abjad.Score():
                item = converted_event
            case _:
                raise NotImplementedError(converted_event)

        self.score_block.items.append(item)

        if reset_tests:
            abjad.persist.as_png(self.lilypond_file, png_ok_path, remove_ly=True)
            ly_test_path = ly_ok_path

        abjad.persist.as_ly(self.lilypond_file, ly_test_path)

        ly_ok, ly_test = pathstr(ly_ok_path), pathstr(ly_test_path)
        failed = ly_ok != ly_test

        if failed or force_png:
            abjad.persist.as_png(
                self.lilypond_file, png_file_path=png_test_path, remove_ly=False
            )
        else:
            try:
                os.remove(png_test_path)
            except FileNotFoundError:
                pass

        if failed:
            diff = difflib.unified_diff(
                ly_ok.splitlines(),
                ly_test.splitlines(),
                lineterm="",
                fromfile=ly_ok_path,
                tofile=ly_test_path,
            )
            self.fail("ly file differs:\n\n{}".format("\n".join(tuple(diff))))

        elif not reset_tests:
            os.remove(ly_test_path)

    # NOTE: Prevent circular import exception, we can't import
    # abjad_converters at top-level. The import order is
    #
    #   abjad_utilities => abjad_parameters => abjad_converters
    #
    # because 'abjad_utilities' provides exceptions to be used
    # by all other modules.
    @functools.cached_property
    def _abjad_converters(self):
        return __import__("mutwo.abjad_converters").abjad_converters


def _parse_event(ev):
    match ev:
        case music_events.NoteLike():
            ev = core_events.Consecution([ev])
        case core_events.Consecution():
            ev = ev
        case core_events.Concurrence():
            ev = ev
        case _:
            raise NotImplementedError(type(ev))
    return ev


def run_if_ekmelily_available(method_to_wrap: typing.Callable):
    """Decorator which only runs test if ekmelily is found"""
    try:
        from mutwo import ekmelily_converters  # type: ignore

        ekmelily_found = True
    except ImportError:
        ekmelily_found = False

    def test(*args, **kwargs):
        if ekmelily_found:
            return method_to_wrap(*args, **kwargs)

    return test


def pathstr(path: str):
    with open(path, "r") as f:
        # Skip the first line, because this is the version statement.
        # We shouldn't compare the version statement, as this breaks
        # tests when running with a different lilypond version.
        return "\n".join((f.read()).splitlines()[1:])
