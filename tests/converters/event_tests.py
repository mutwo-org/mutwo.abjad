"""Test conversion of mutwo to abjad events"""

import os
import unittest

import abjad  # type: ignore

try:
    import quicktions as fractions  # type: ignore
except ImportError:
    import fractions  # type: ignore

from mutwo import abjad_converters
from mutwo import abjad_utilities
from mutwo import core_events
from mutwo import core_parameters
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
    base_path = f"{abjad_utilities.AbjadTestCase.base_path}{os.sep}events"

    @t(RESET_TESTS)
    def test_integration(self):
        return dict(
            converter=_make_complex_converter(), ev=_make_complex_sequential_event()
        )

    @t(RESET_TESTS)
    def test_tempo(self):
        tempo_envelope = core_events.Envelope(
            (
                (0, core_parameters.DirectTempoPoint((30, 50), 2)),
                (2, core_parameters.DirectTempoPoint((30, 50), 2)),
            )
        )
        return dict(
            converter=abjad_converters.SequentialEventToAbjadVoice(
                abjad_converters.LeafMakerSequentialEventToQuantizedAbjadContainer(),
                default_tempo_envelope=tempo_envelope,
            ),
            ev=seq([n("c", 1), n("c", 1), n("c", 1)]),
        )

    @t(RESET_TESTS)
    def test_grace_note(self):
        def mn(**kwargs):
            return n("c", 1, **kwargs)

        return dict(
            converter=abjad_converters.SequentialEventToAbjadVoice(
                abjad_converters.LeafMakerSequentialEventToQuantizedAbjadContainer()
            ),
            ev=seq(
                [
                    mn(
                        grace_note_sequential_event=seq([n("d", 0.125), n("e", 0.125)]),
                    ),
                    mn(
                        after_grace_note_sequential_event=seq(
                            [n("d", 0.125), n("e", 0.125), n("f", 0.125)]
                        ),
                    ),
                    mn(),
                    mn(grace_note_sequential_event=seq([n("d", 0.125), n("e", 0.125)])),
                ]
            ),
        )

    @t(RESET_TESTS)
    def test_first_grace_note_no_flag(self):
        return dict(
            converter=abjad_converters.SequentialEventToAbjadVoice(
                abjad_converters.LeafMakerSequentialEventToDurationLineBasedQuantizedAbjadContainer()
            ),
            ev=seq(
                [
                    n(
                        "c",
                        grace_note_sequential_event=seq([n("d", f(1, 8))]),
                    )
                ]
            ),
        )

    @t(RESET_TESTS)
    def test_lyric(self):
        lbl = music_parameters.LanguageBasedLyric
        lbs = music_parameters.LanguageBasedSyllable
        return dict(
            converter=abjad_converters.SequentialEventToAbjadVoice(
                abjad_converters.LeafMakerSequentialEventToQuantizedAbjadContainer()
            ),
            ev=seq(
                [
                    n([], 1),
                    n("c", 1, lyric=lbl("helloT")),
                    n("d", f(1, 8), lyric=lbl("")),
                    n("e", f(1, 4), lyric=lbl("i")),
                    n("e", f(3, 8), lyric=lbs(False, "ho")),
                    n("e", f(1, 4), lyric=lbs(True, "pe")),
                ]
            ),
        )

    @t(RESET_TESTS)
    def test_duration_line(self):
        return dict(
            converter=abjad_converters.SequentialEventToAbjadVoice(
                abjad_converters.NauertSequentialEventToDurationLineBasedQuantizedAbjadContainer()
            ),
            ev=seq(
                [
                    n([], 1),
                    n("c", 0.125),
                    n("d", 1),
                    n([], 0.375),
                    n("e", 0.25),
                    n("d", 0.5),
                    n("c", 0.75),
                    n("a", 0.25),
                ]
            ),
        )

    @t(RESET_TESTS)
    def test_multimeasure_rest(self):
        """Test that mutwo.abjad creats MultimeasureRest for empty bar"""
        ev = seq(
            [
                n(duration=fractions.Fraction(3, 4)),
            ]
        )
        return dict(
            converter=abjad_converters.SequentialEventToAbjadVoice(
                abjad_converters.LeafMakerSequentialEventToQuantizedAbjadContainer(
                    default_time_signature_sequence=(abjad.TimeSignature((3, 4)),)
                )
            ),
            ev=ev,
        )

    @t(RESET_TESTS)
    def test_multimeasure_rest_with_indicators(self):
        """Test that indicators survive on a multi measure rest

        For some reasons it's not possible to place indicators on multi measure
        rests. Therefore mutwo.abjad needs to ensure not to place multi measure
        rests in places where indicators were added.
        """
        ev = seq(
            [
                n(duration=fractions.Fraction(3, 4)),
            ]
        )
        ev[0].playing_indicator_collection.fermata.type = "fermata"
        return dict(
            converter=abjad_converters.SequentialEventToAbjadVoice(
                abjad_converters.LeafMakerSequentialEventToQuantizedAbjadContainer(
                    default_time_signature_sequence=(abjad.TimeSignature((3, 4)),)
                )
            ),
            ev=ev,
        )

    @t(RESET_TESTS)
    def test_nested_event(self):
        return dict(converter=_make_nested_converter(), ev=_make_nested_event())

    def _test_tuplet(self, ev: core_events.SequentialEvent):
        return dict(
            converter=abjad_converters.SequentialEventToAbjadVoice(
                abjad_converters.LeafMakerSequentialEventToQuantizedAbjadContainer(
                    default_time_signature_sequence=(abjad.TimeSignature((4, 4)),)
                )
            ),
            ev=ev,
        )

    @t(RESET_TESTS)
    def test_tuplet_simple(self):
        """Test that tuplets work

        Test if a simple tuplet that spans across one bar works.
        """
        return self._test_tuplet(
            seq(
                [
                    # We start with very simple tuplets,
                    # that span across the full bar.
                    n("c", f(1, 6)),
                    n("d", f(1, 6)),
                    n("e", f(1, 12)),
                    n("f", f(1, 12)),
                    n("g", f(1, 24)),
                    n("a", f(1, 12)),
                    n("b", f(1, 24)),
                    n("c5", f(1, 6)),
                    n("d5", f(1, 12)),
                    n("e5", f(1, 12)),
                ]
            )
        )

    @t(RESET_TESTS)
    def test_tuplet_two_prolations_in_one_bar(self):
        """Test if two different tuplets within one bar works."""
        return self._test_tuplet(
            seq(
                [
                    n("c", f(1, 10)),
                    n("c", f(1, 10)),
                    n("c", f(1, 10)),
                    n("c", f(1, 5)),
                    n("c", f(1, 6)),
                    n("d", f(1, 6)),
                    n("d", f(1, 6)),
                ]
            )
        )

    @t(RESET_TESTS)
    def test_tuplet_concatenation(self):
        """Test if follow-up notes concatenate together.

        In some cases, there are multiple easier understandings what a certain
        duration can be, and in those cases tuplets won't be together, but
        broke up, even in simple cases as the example below. To fix this
        LeafMakerSequentialEventToQuantizedAbjadContainer has an extra routine
        ('_concatenate_adjacent_tuplets'). This test checks if this routine
        still works.
        """
        return self._test_tuplet(
            seq(
                [
                    n("c", f(1, 4)),
                    n("c", f(1, 12)),
                    n("c", f(1, 12)),
                    # The following note should be part of the current
                    # tuplet, it sustains in this tuplet. But without
                    # an explicit tuplet - concatenation, this note
                    # won't be part of the given tuplet, the tuplet
                    # is split into before this 1/4 and afterwards. Why?
                    # Because 1/4 can also represented as a not-tuplet.
                    n("c", f(1, 4)),
                    n("c", f(1, 12)),
                ]
            )
        )

    @t(RESET_TESTS)
    def test_nested_tuplet(self):
        """Test if nested tuplets are supported."""
        return self._test_tuplet(
            seq(
                [
                    n("c", f(3, 4)),
                    # Let's divide the last quarter note
                    # into 5: so we have 1/5 // 4 = 1/20.
                    n("c", f(1, 20)),
                    n("c", f(1, 20)),
                    n("c", f(1, 10)),
                    # And then, to make it even more complicated,
                    # we divide the last 1/20 into 3: so we have
                    # a nested tuplet of 5 => 3. But because
                    # LeafMakerSequentialEventToQuantizedAbjadContainer
                    # doesn't support nested tuplets, this looks
                    # strange. But that's expected, because it's
                    # not supported yet.
                    n("d", f(1, 60)),
                    n("d", f(1, 60)),
                    n("d", f(1, 60)),
                ]
            )
        )

    @t(RESET_TESTS)
    def test_ties_across_tuplets_in_two_different_bars(self):
        """Test if ties across two tuplets in two different bars work"""
        return self._test_tuplet(
            seq(
                [
                    n("c", f(3, 4)),
                    n("c", f(1, 6)),
                    n("c", f(1, 6)),
                    n("c", f(1, 6)),
                ]
            )
        )

    @t(RESET_TESTS)
    def test_ties_across_tuplets_with_different_prolation(self):
        """Test if ties across two tuplets with different prolation works

        LeafMakerSequentialEventToQuantizedAbjadContainer doesn't support
        this yet: this looks broke.
        """
        return self._test_tuplet(
            seq(
                [
                    n("c", f(1, 6)),
                    n("c", f(1, 6)),
                    n("c", f(1, 6) + f(1, 20)),  # this is the tied note
                    n("c", f(1, 20)),
                    n("c", f(3, 20)),
                ]
            )
        )


f = fractions.Fraction
n = music_events.NoteLike
seq = core_events.SequentialEvent
tsim = core_events.TaggedSimultaneousEvent


class SequentialEventToAbjadVoiceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # initialise converter and sequential event for simple tests
        cls.converter = abjad_converters.SequentialEventToAbjadVoice()
        cls.sequential_event = core_events.SequentialEvent(
            [
                music_events.NoteLike(pitch_name, duration=duration, volume="mf")
                for pitch_name, duration in (
                    ("c", 0.75),
                    ("a", 0.25),
                    ("g", 1 / 6),
                    ("es", 1 / 12),
                )
            ]
        )
        # initialise complex converter and sequential event for complex tests
        cls.complex_converter = _make_complex_converter()
        cls.complex_sequential_event = _make_complex_sequential_event()

    def test_convert(self):
        expected_abjad_voice = abjad.Voice(
            [
                abjad.score.Container("c'2. a'4"),
                abjad.score.Container(
                    [abjad.Tuplet(components="g'4 es'8"), abjad.Rest("r2.")]
                ),
            ]
        )
        abjad.attach(abjad.TimeSignature((4, 4)), expected_abjad_voice[0][0])
        abjad.attach(
            abjad.MetronomeMark(reference_duration=(1, 4), units_per_minute=120),
            expected_abjad_voice[0][0],
        )
        abjad.attach(abjad.Dynamic("mf"), expected_abjad_voice[0][0])

        converted_sequential_event = self.converter.convert(self.sequential_event)

        # complex comparison because == raises Error (although leaves are equal)
        for component0, component1 in zip(
            abjad.select.components(expected_abjad_voice),
            abjad.select.components(converted_sequential_event),
        ):
            self.assertEqual(type(component0), type(component1))
            if hasattr(component0, "written_duration"):
                self.assertEqual(
                    component0.written_duration, component1.written_duration
                )
            if isinstance(component0, abjad.Note):
                self.assertEqual(component0.written_pitch, component1.written_pitch)

            indicators0, indicators1 = (
                # filter out q_events annotations
                [
                    indicator
                    for indicator in abjad.get.indicators(component)
                    if type(indicator) != dict
                ]
                for component in (component0, component1)
            )

            self.assertEqual(indicators0, indicators1)


class NestedComplexEventToAbjadContainerTest(abjad_utilities.AbjadTestCase):
    def test_convert(self):
        # an integration test (testing if the rendered png
        # is equal to the previously rendered and manually checked png)

        converter = _make_nested_converter()
        abjad_score = converter.convert(_make_nested_event())

        # check if abjad container type is correct
        self.assertEqual(type(abjad_score), abjad.Score)

        # check if abjad container name is correct
        self.assertEqual(abjad_score.name, "Integrating duo")


def _make_nested_event() -> core_events.TaggedSimultaneousEvent:
    w = music_parameters.WesternPitch
    return tsim(
        [
            tsim(
                [
                    seq(
                        [
                            n(p, d)
                            for p, d in zip("c d e f g a b".split(" "), (1 / 4,) * 7)
                        ]
                    ),
                    seq([n(p, d) for p, d in [[w("c", 3), 1 / 2]] * 4]),
                ],
                tag="Piano",
            ),
            tsim(
                [
                    seq([n(p, d) for p, d in [[w("es", 5), 1 / 2]] * 4]),
                    seq([n(p, d) for p, d in [[w("b", 3), 1 / 2]] * 4]),
                ],
                tag="Violin",
            ),
        ],
        tag="Integrating duo",
    )


def _make_nested_converter():
    return abjad_converters.NestedComplexEventToAbjadContainer(
        abjad_converters.TagBasedNestedComplexEventToComplexEventToAbjadContainers(
            {
                "Piano": abjad_converters.NestedComplexEventToAbjadContainer(
                    abjad_converters.CycleBasedNestedComplexEventToComplexEventToAbjadContainers(
                        [
                            abjad_converters.SequentialEventToAbjadVoice(
                                abjad_converters.LeafMakerSequentialEventToQuantizedAbjadContainer()
                            ),
                        ]
                    ),
                    abjad.StaffGroup,
                    "PianoStaff",
                    post_process_abjad_container_routine_sequence=(
                        abjad_converters.AddInstrumentName(
                            complex_event_to_instrument_name=lambda complex_event: complex_event.tag
                        ),
                    ),
                ),
                "Violin": abjad_converters.NestedComplexEventToAbjadContainer(
                    abjad_converters.CycleBasedNestedComplexEventToComplexEventToAbjadContainers(
                        [
                            abjad_converters.SequentialEventToAbjadVoice(),
                        ]
                    ),
                    abjad.Staff,
                    "Staff",
                    post_process_abjad_container_routine_sequence=(
                        abjad_converters.AddInstrumentName(
                            complex_event_to_instrument_name=lambda complex_event: complex_event.tag
                        ),
                    ),
                ),
            }
        ),
        abjad.Score,
        "Score",
    )


def _make_complex_converter():
    return abjad_converters.SequentialEventToAbjadVoice(
        abjad_converters.LeafMakerSequentialEventToQuantizedAbjadContainer(
            default_time_signature_sequence=[
                abjad.TimeSignature(ts)
                for ts in (
                    (4, 4),
                    (4, 4),
                    (4, 4),
                    (4, 4),
                    (4, 4),
                    (4, 4),
                    (4, 4),
                    (3, 4),
                    (6, 8),
                    (3, 4),
                )
            ],
        ),
        default_tempo_envelope=core_events.Envelope(
            ((0, 120), (3, 120), (5, 130), (7.75, 130), (7.75, 100))
        ),
    )


def _make_complex_sequential_event() -> core_events.SequentialEvent[
    music_events.NoteLike
]:
    e = seq(
        [
            music_events.NoteLike(pitch_name, duration=duration, volume="mf")
            for pitch_name, duration in (
                ("c f a d", 0.75),
                ("a", 0.25),
                ("g", fractions.Fraction(1, 12)),
                ("es", fractions.Fraction(1, 12)),
                ("fqs bf bqf", fractions.Fraction(1, 12)),
                ("c", fractions.Fraction(3, 4)),
                ([], 1),  # full measure rest
                ("ds", 0.75),
                ([], fractions.Fraction(3, 8)),
                ("1/3", 0.75),
                ([], 0.25),
                ("1/7", 1.5),
                ("5/4", 0.25),
                ("7/4", fractions.Fraction(1, 8)),
                ([], fractions.Fraction(3, 4)),
                ("c", fractions.Fraction(1, 4)),
                ("c", fractions.Fraction(1, 4)),
                ("c", fractions.Fraction(1, 4)),
                ("c", fractions.Fraction(1, 4)),
                ("c", fractions.Fraction(1, 4)),
                ("c", fractions.Fraction(1, 4)),
            )
        ]
    )

    e[0].notation_indicator_collection.margin_markup.content = "Magic Instr"
    e[2].playing_indicator_collection.bartok_pizzicato.is_active = True
    e[3].volume = "fff"
    e[4].volume = "fff"
    e[7].playing_indicator_collection.fermata.type = "fermata"
    e[9].notation_indicator_collection.ottava.octave_count = -1
    e[9].playing_indicator_collection.string_contact_point.contact_point = "sul tasto"
    e[11].playing_indicator_collection.string_contact_point.contact_point = "sul tasto"
    e[11].notation_indicator_collection.ottava.octave_count = -2
    e[12].playing_indicator_collection.string_contact_point.contact_point = "pizzicato"
    return e


def get_tests_path() -> str:
    return "/".join(os.path.abspath(__file__).split("/")[:-1])


if __name__ == "__main__":
    unittest.main()
