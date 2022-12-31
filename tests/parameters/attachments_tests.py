import os
import typing

import quicktions as fractions

from mutwo import abjad_utilities
from mutwo import core_events
from mutwo import music_events
from mutwo import music_parameters


t = abjad_utilities.AbjadTestCase.t

# Set to `True` if all images should be replaced
# by new images.
# Can be useful in case Lilypond renderings change
# in minor ways, but human checks resolved that
# the content is still the same.
RESET_TESTS = False


class IntegrationTest(abjad_utilities.AbjadTestCase):
    base_path = f"{abjad_utilities.AbjadTestCase.base_path}{os.sep}parameters"

    @t(RESET_TESTS)
    def test_arpeggio(self):
        def get_ev(direction):
            return mp(
                n("5/8 3/4 1/1", f(5, 8)),
                lambda p: setattr(p.arpeggio, "direction", direction),
            )

        return dict(ev=seq([get_ev("up"), get_ev("down")]))

    @t(RESET_TESTS)
    def test_articulation(self):
        def get_ev(name):
            return mp(
                n("c f", f(5, 8)),
                lambda p: setattr(p.articulation, "name", name),
            )

        return dict(ev=seq([get_ev("."), get_ev("tenuto")]))


n = music_events.NoteLike
seq = core_events.SequentialEvent
f = fractions.Fraction


def mp(
    note_like: music_events.NoteLike,
    function: typing.Callable[
        [music_parameters.PlayingIndicatorCollection], type[None]
    ],
):
    function(note_like.playing_indicator_collection)
    return note_like
