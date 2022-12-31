import functools
import operator
import os
import math
import typing
import unittest

try:
    from PIL import Image  # type: ignore
    from PIL import ImageChops  # type: ignore
except ImportError:
    pass

import abjad

from mutwo import abjad_converters
from mutwo import core_events
from mutwo import music_events


__all__ = ("AbjadTestCase", "run_if_ekmelily_available")


class AbjadTestCase(unittest.TestCase):
    base_path = f"tests{os.sep}img"

    @staticmethod
    def t(reset_tests: bool = False, remove_ly: bool = True):
        def t(test_method: typing.Callable):
            return lambda self: self._test(
                test_method.__name__, reset_tests, remove_ly, **test_method(self)
            )

        return t

    def assertImagesEqual(self, path0: str, path1: str):
        image0, image1 = (Image.open(path) for path in (path0, path1))
        difference = ImageChops.difference(image1, image0)
        self.assertTrue(difference.getbbox() is None, "Images differ!")

    def assertImagesAlmostEqual(
        self, image0: Image, image1: Image, tolerance: float = 0.01
    ):
        d = root_mean_square_difference(image0, image1)
        self.assertTrue(
            d < tolerance, f"Images differ above tolerance: '{d} >= '{tolerance}'!"
        )

    def setUp(self):
        header_block = abjad.Block(name="header")
        header_block.items.append('tagline = "---integration-test---"')
        self.lilypond_file = abjad.LilyPondFile()
        self.score_block = abjad.Block(name="score")
        self.lilypond_file.items.append(r'\include "lilypond-book-preamble.ly"')
        self.lilypond_file.items.extend([header_block, self.score_block])

    def _test(
        self,
        name: str,
        reset_tests: bool = False,
        remove_ly: bool = True,
        converter: abjad_converters.SequentialEventToAbjadVoice = abjad_converters.SequentialEventToAbjadVoice(),
        ev: core_events.abc.Event = core_events.SequentialEvent(
            [core_events.SimpleEvent(1)]
        ),
        tolerance: float = 0.1,
    ):

        converted_event = converter.convert(_parse_event(ev))

        base_p = self.base_path
        file_ok_path = f"{base_p}{os.sep}{name}_ok.png"
        file_test_path = f"{base_p}{os.sep}{name}_test.png"

        if reset_tests:
            file_test_path = file_ok_path

        match converted_event:
            case abjad.Voice():
                item = abjad.Staff([converted_event])
            case abjad.Score():
                item = converted_event
            case _:
                raise NotImplementedError(converted_event)

        self.score_block.items.append(item)

        abjad.persist.as_png(
            self.lilypond_file, png_file_path=file_test_path, remove_ly=remove_ly
        )

        image_ok, image_test = (Image.open(p) for p in (file_ok_path, file_test_path))

        if tolerance > 0:
            self.assertImagesAlmostEqual(image_ok, image_test, tolerance)
        else:
            self.assertImagesEqual(image_ok, image_test)

        if not reset_tests:
            os.remove(file_test_path)


def _parse_event(ev):
    match ev:
        case music_events.NoteLike():
            ev = core_events.SequentialEvent([ev])
        case core_events.SequentialEvent():
            ev = ev
        case core_events.SimultaneousEvent():
            ev = ev
        case _:
            raise NotImplementedError(type(ev))
    return ev


def root_mean_square_difference(image0: Image, image1: Image):
    """Calculate root-mean-square difference between two images.

    Taken from: http://snipplr.com/view/757/compare-two-pil-images-in-python/
    """
    h0, h1 = (i.histogram() for i in (image0, image1))

    def mean_square(a: float, b: float) -> float:
        if not a:
            a = 0.0
        if not b:
            b = 0.0
        return (a - b) ** 2

    return math.sqrt(
        functools.reduce(operator.add, map(mean_square, h0, h1))
        / (image0.size[0] * image0.size[1])
    )


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
