import os
import typing

import abjad

try:
    import quicktions as fractions
except ImportError:
    import fractions

from mutwo import abjad_converters
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

# Set to `True` to export png files for each test even
# when the test doesn't fail (to check if png output still
# matches expected output).
FORCE_PNG = False


class IntegrationTest(abjad_utilities.AbjadTestCase):
    base_path = f"{abjad_utilities.AbjadTestCase.base_path}{os.sep}parameters"

    @t(RESET_TESTS, FORCE_PNG)
    def test_arpeggio(self):
        def get_ev(direction):
            return mp(
                n("5/8 3/4 1/1", f(5, 8)),
                lambda p: setattr(p.arpeggio, "direction", direction),
            )

        return dict(
            ev=seq([get_ev("up"), get_ev("down")]),
            converter=abjad_converters.SequentialEventToAbjadVoice(
                abjad_converters.NauertSequentialEventToQuantizedAbjadContainer()
            ),
        )

    @t(RESET_TESTS, FORCE_PNG)
    def test_articulation(self):
        def get_ev(name):
            return mp(
                n("c f", f(5, 8)),
                lambda p: setattr(p.articulation, "name", name),
            )

        return dict(
            ev=seq([get_ev("."), get_ev("tenuto")]),
            converter=abjad_converters.SequentialEventToAbjadVoice(
                abjad_converters.NauertSequentialEventToQuantizedAbjadContainer()
            ),
        )

    @t(RESET_TESTS, FORCE_PNG)
    def test_tremolo(self):
        return dict(
            ev=seq(
                [
                    mp(
                        n("b", f(5, 8)),
                        lambda p: setattr(p.tremolo, "flag_count", 16),
                    )
                ]
            ),
            converter=abjad_converters.SequentialEventToAbjadVoice(
                abjad_converters.NauertSequentialEventToQuantizedAbjadContainer()
            ),
        )

    @t(RESET_TESTS, FORCE_PNG)
    def test_articifical_harmonic(self):
        return dict(
            ev=mp(
                n("c", f(7, 8)),
                lambda p: setattr(p.artifical_harmonic, "semitone_count", 5),
            )
        )

    @t(RESET_TESTS, FORCE_PNG)
    def test_natural_harmonic_node_list(self):
        return dict(
            ev=self._get_natural_harmonic_node_list_ev(),
            converter=abjad_converters.SequentialEventToAbjadVoice(
                abjad_converters.NauertSequentialEventToQuantizedAbjadContainer()
            ),
        )

    @t(RESET_TESTS, FORCE_PNG)
    def test_natural_harmonic_node_list_with_duration_line(self):
        return dict(
            ev=self._get_natural_harmonic_node_list_ev(),
            converter=abjad_converters.SequentialEventToAbjadVoice(
                abjad_converters.LeafMakerSequentialEventToDurationLineBasedQuantizedAbjadContainer()
            ),
        )

    @t(RESET_TESTS, FORCE_PNG)
    def test_first_natural_harmonic_node_list_without_duplicates(self):
        return dict(
            ev=self._get_natural_harmonic_node_list_ev()[2:3],
        )

    def _get_natural_harmonic_node_list_ev(self):
        def e(*node, **kwargs):
            e = n("c", f(5, 16))
            nhn_l = e.playing_indicator_collection.natural_harmonic_node_list
            for v, k in kwargs.items():
                setattr(nhn_l, v, k)
            nhn_l.extend(node)
            return e

        h0_tuple = music_parameters.String(
            music_parameters.JustIntonationPitch("3/4"),
            music_parameters.WesternPitch("g", 3),
        ).natural_harmonic_tuple

        h1_tuple = music_parameters.String(
            music_parameters.JustIntonationPitch("9/8"),
            music_parameters.WesternPitch("d", 4),
        ).natural_harmonic_tuple

        return seq(
            [
                e(h0_tuple[0].node_tuple[0], parenthesize_lower_note_head=True),
                n(),
                e(h0_tuple[1].node_tuple[0], h1_tuple[1].node_tuple[0]),
                e(h0_tuple[0].node_tuple[0], write_string=False),
            ]
        )

    @t(RESET_TESTS, FORCE_PNG)
    def test_string_contact_point(self):
        def e(name):
            return mp(
                n("a", f(5, 8)),
                lambda p: setattr(p.string_contact_point, "contact_point", name),
            )

        def o():
            return e("ordinario")

        def p():
            return e("pizzicato")

        return dict(
            ev=seq([o(), p(), p(), p(), o()]),
            converter=abjad_converters.SequentialEventToAbjadVoice(
                abjad_converters.NauertSequentialEventToQuantizedAbjadContainer()
            ),
        )

    @t(RESET_TESTS, FORCE_PNG)
    def test_trill(self):
        return dict(
            ev=mp(
                n("c", f(7, 8)),
                lambda p: setattr(p.trill, "pitch", music_parameters.WesternPitch("d")),
            )
        )

    @t(RESET_TESTS, FORCE_PNG)
    def test_cue(self):
        return dict(ev=mp(n("c", f(7, 8)), lambda p: setattr(p.cue, "index", 4)))

    @t(RESET_TESTS, FORCE_PNG)
    def test_woodwind_fingering(self):
        def s(p, key, value):
            setattr(p.woodwind_fingering, key, value)

        def s_tuple(p, *s_tuple):
            [s(p, key, value) for key, value in s_tuple]

        return dict(
            ev=mp(
                n("c", f(7, 8)),
                lambda p: s_tuple(
                    p,
                    ("cc", "one two three four six".split(" ")),
                    ("left_hand", ("low-bes",)),
                    ("right_hand", ("low-c", "high-fis")),
                    ("instrument", "alto-saxophone"),
                ),
            )
        )

    @t(RESET_TESTS, FORCE_PNG)
    def test_pedal(self):
        def e(p, activity, type):
            e = n(p, f(5, 8))
            p = e.playing_indicator_collection.pedal
            p.pedal_activity = activity
            p.pedal_type = type
            return e

        def sus0():
            return e("a", False, "sustain")

        def sus1():
            return e("a", True, "sustain")

        def corda0():
            return e("g", False, "corda")

        def corda1():
            return e("g", True, "corda")

        return dict(
            ev=seq([sus1(), sus1(), sus0(), corda1(), corda1(), corda0()]),
            converter=abjad_converters.SequentialEventToAbjadVoice(
                abjad_converters.NauertSequentialEventToQuantizedAbjadContainer()
            ),
        )

    @t(RESET_TESTS, FORCE_PNG)
    def test_hairpin(self):
        def h(simple_event):
            return simple_event.playing_indicator_collection.hairpin

        e = seq(
            [
                n("c", f(3, 4)),
                n("d", f(1, 4)),
                n("e", f(1, 4)),
                n("e", f(5, 4)),
                n([], f(1, 8)),
            ]
        )

        h(e[0]).symbol = "<>"
        h(e[0]).niente = True
        h(e[1]).symbol = "<"
        h(e[1]).niente = True
        h(e[2]).symbol = ">"
        h(e[3]).symbol = "<>"
        h(e[3]).niente = True
        h(e[4]).symbol = "!"

        return dict(ev=e)

    @t(RESET_TESTS, FORCE_PNG)
    def test_bartok_pizzicato(self):
        return dict(
            ev=mp(n("c", f(7, 8)), lambda p: setattr(p, "bartok_pizzicato", True))
        )

    @t(RESET_TESTS, FORCE_PNG)
    def test_breath_mark(self):
        return dict(
            ev=seq(
                [n(), mp(n("c", f(7, 8)), lambda p: setattr(p, "breath_mark", True))]
            )
        )

    @t(RESET_TESTS, FORCE_PNG)
    def test_fermata(self):
        def e(type):
            return mp(n("c", f(7, 8)), lambda p: setattr(p.fermata, "type", type))

        return dict(ev=seq([e("fermata"), e("longfermata")]))

    @t(RESET_TESTS, FORCE_PNG)
    def test_prall(self):
        return dict(ev=mp(n("c", f(7, 8)), lambda p: setattr(p, "prall", True)))

    @t(RESET_TESTS, FORCE_PNG)
    def test_tie(self):
        return dict(
            ev=seq([mp(n("c", f(7, 8)), lambda p: setattr(p, "tie", True)), n("c")])
        )

    @t(RESET_TESTS, FORCE_PNG)
    def test_glissando(self):
        return dict(
            ev=seq(
                [mp(n("c", f(7, 8)), lambda p: setattr(p, "glissando", True)), n("d")]
            )
        )

    @t(RESET_TESTS, FORCE_PNG)
    def test_bend_after(self):
        return dict(
            ev=mp(n("c", f(7, 8)), lambda p: setattr(p.bend_after, "bend_amount", 3))
        )

    @t(RESET_TESTS, FORCE_PNG)
    def test_laissez_vibrer(self):
        return dict(
            ev=mp(n("c", f(7, 8)), lambda p: setattr(p, "laissez_vibrer", True))
        )

    @t(RESET_TESTS, FORCE_PNG)
    def test_ornamenation(self):
        e = n("c", f(5, 16))
        o = e.playing_indicator_collection.ornamentation
        o.count = 3
        o.direction = "up"
        return dict(ev=e)

    @t(RESET_TESTS, FORCE_PNG)
    def test_bar_line(self):
        return dict(
            ev=seq(
                [
                    mn(n("c", 1), lambda n: setattr(n.bar_line, "abbreviation", "!")),
                    n("d", 0.5),
                ]
            )
        )

    @t(RESET_TESTS, FORCE_PNG)
    def test_clef(self):
        return dict(ev=mn(n("c", f(5, 16)), lambda n: setattr(n.clef, "name", "bass")))

    @t(RESET_TESTS, FORCE_PNG)
    def test_ottava(self):
        return dict(
            ev=mn(
                n(music_parameters.WesternPitch("c", 6), f(5, 16)),
                lambda n: setattr(n.ottava, "octave_count", 1),
            )
        )

    @t(RESET_TESTS, FORCE_PNG)
    def test_markup(self):
        e = n("c", f(5, 16))
        m = e.notation_indicator_collection.markup
        m.content = r'\markup { "This is a test!" }'
        m.direction = abjad.enums.UP
        return dict(ev=e)

    @t(RESET_TESTS, FORCE_PNG)
    def test_rehearsal_mark(self):
        return dict(
            ev=mn(
                n("c", f(5, 16)),
                lambda n: setattr(n.rehearsal_mark, "markup", "RM"),
            )
        )

    @t(RESET_TESTS, FORCE_PNG)
    def test_margin_markup(self):
        return dict(
            ev=mn(
                n("c", f(5, 16)), lambda n: setattr(n.margin_markup, "content", "test")
            )
        )


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


def mn(
    note_like: music_events.NoteLike,
    function: typing.Callable[
        [music_parameters.PlayingIndicatorCollection], type[None]
    ],
):
    function(note_like.notation_indicator_collection)
    return note_like
