import os
import typing
import unittest

from PIL import Image  # type: ignore
from PIL import ImageChops  # type: ignore

import abjad  # type: ignore
import expenvelope  # type: ignore

try:
    import quicktions as fractions  # type: ignore
except ImportError:
    import fractions  # type: ignore

from mutwo import abjad_converters
from mutwo import abjad_parameters
from mutwo import core_events
from mutwo import core_parameters
from mutwo import music_events
from mutwo import music_parameters


def run_if_ekmelily_is_available(method_to_wrap: typing.Callable):

    try:
        from mutwo import ekmelily_converters  # type: ignore

        ekmelily_found = True
    except ImportError:
        ekmelily_found = False

    def test(*args, **kwargs):
        if ekmelily_found:
            return method_to_wrap(*args, **kwargs)

    return test


class MutwoPitchToAbjadPitchTest(unittest.TestCase):
    def test_convert(self):
        converter = abjad_converters.MutwoPitchToAbjadPitch()
        self.assertEqual(
            converter.convert(music_parameters.WesternPitch("ds", 4)),
            abjad.NamedPitch("ds'"),
        )
        self.assertEqual(
            converter.convert(music_parameters.WesternPitch("gf", 5)),
            abjad.NamedPitch("gf''"),
        )
        self.assertEqual(
            converter.convert(
                music_parameters.JustIntonationPitch("3/2", concert_pitch=262)
            ),
            abjad.NumberedPitch(7),
        )
        self.assertEqual(
            converter.convert(
                music_parameters.JustIntonationPitch("3/4", concert_pitch=262)
            ),
            abjad.NumberedPitch(-5),
        )
        self.assertEqual(
            converter.convert(
                music_parameters.JustIntonationPitch("5/4", concert_pitch=262)
            ),
            abjad.NumberedPitch(4),
        )


class MutwoPitchToHEJIAbjadPitchTest(unittest.TestCase):
    @run_if_ekmelily_is_available
    def test_convert(self):
        converter = abjad_converters.MutwoPitchToHEJIAbjadPitch(reference_pitch="c")
        self.assertEqual(
            abjad.lilypond(
                converter.convert(music_parameters.JustIntonationPitch("1/1"))
            ),
            abjad.lilypond(abjad.NamedPitch("c'")),
        )
        self.assertEqual(
            abjad.lilypond(
                converter.convert(music_parameters.JustIntonationPitch("3/2"))
            ),
            abjad.lilypond(abjad.NamedPitch("g'")),
        )
        self.assertEqual(
            abjad.lilypond(
                converter.convert(music_parameters.JustIntonationPitch("5/4"))
            ),
            "eoaa'",
        )
        self.assertEqual(
            abjad.lilypond(
                converter.convert(music_parameters.JustIntonationPitch("7/4"))
            ),
            "bfoba'",
        )
        self.assertEqual(
            abjad.lilypond(
                converter.convert(music_parameters.JustIntonationPitch("7/6"))
            ),
            "efoba'",
        )
        self.assertEqual(
            abjad.lilypond(
                converter.convert(music_parameters.JustIntonationPitch("12/7"))
            ),
            "auba'",
        )
        self.assertEqual(
            abjad.lilypond(
                converter.convert(music_parameters.JustIntonationPitch("9/8"))
            ),
            "d'",
        )
        self.assertEqual(
            abjad.lilypond(
                converter.convert(music_parameters.JustIntonationPitch("9/16"))
            ),
            "d",
        )
        self.assertEqual(
            abjad.lilypond(
                converter.convert(music_parameters.JustIntonationPitch("9/4"))
            ),
            "d''",
        )
        self.assertEqual(
            abjad.lilypond(
                converter.convert(music_parameters.JustIntonationPitch("32/33"))
            ),
            "cuca'",
        )
        self.assertEqual(
            abjad.lilypond(
                converter.convert(music_parameters.JustIntonationPitch("49/50"))
            ),
            "dffuabobb'",
        )


class MutwoVolumeToAbjadAttachmentDynamicTest(unittest.TestCase):
    def test_convert(self):
        converter = abjad_converters.MutwoVolumeToAbjadAttachmentDynamic()
        self.assertEqual(
            converter.convert(music_parameters.WesternVolume("mf")),
            abjad_parameters.Dynamic("mf"),
        )
        self.assertEqual(
            converter.convert(music_parameters.WesternVolume("fff")),
            abjad_parameters.Dynamic("fff"),
        )
        self.assertEqual(
            converter.convert(music_parameters.DecibelVolume(-6)),
            abjad_parameters.Dynamic(
                music_parameters.WesternVolume.from_decibel(-6).name
            ),
        )


class MutwoLyricToAbjadStringTest(unittest.TestCase):
    def setUp(self):
        self.mutwo_lyric_to_abjad_string = abjad_converters.MutwoLyricToAbjadString()

    def test_convert_empty_string(self):
        self.assertEqual(
            self.mutwo_lyric_to_abjad_string(music_parameters.DirectLyric("")), "_"
        )

    def test_convert_filled_string(self):
        self.assertEqual(
            self.mutwo_lyric_to_abjad_string(music_parameters.DirectLyric("hello")),
            "hello",
        )

    def test_convert_not_last_syllable(self):
        self.assertEqual(
            self.mutwo_lyric_to_abjad_string(
                music_parameters.LanguageBasedSyllable(False, "hel")
            ),
            "hel --",
        )

    def test_convert_last_syllable(self):
        self.assertEqual(
            self.mutwo_lyric_to_abjad_string(
                music_parameters.LanguageBasedSyllable(True, "lo")
            ),
            "lo",
        )


class ComplexTempoEnvelopeToAbjadAttachmentTempoTest(unittest.TestCase):
    def test_convert_tempo_points(self):
        self.assertEqual(
            abjad_converters.ComplexTempoEnvelopeToAbjadAttachmentTempo._convert_tempo_point_tuple(
                (60, 120, core_parameters.TempoPoint(120, reference=4))
            ),
            (
                core_parameters.TempoPoint(60),
                core_parameters.TempoPoint(120),
                core_parameters.TempoPoint(120, reference=4),
            ),
        )

    def test_find_dynamic_change_indication(self):
        self.assertEqual(
            abjad_converters.ComplexTempoEnvelopeToAbjadAttachmentTempo._find_dynamic_change_indication(
                core_parameters.TempoPoint(120), core_parameters.TempoPoint(130)
            ),
            "acc.",
        )
        self.assertEqual(
            abjad_converters.ComplexTempoEnvelopeToAbjadAttachmentTempo._find_dynamic_change_indication(
                core_parameters.TempoPoint(120), core_parameters.TempoPoint(110)
            ),
            "rit.",
        )
        self.assertEqual(
            abjad_converters.ComplexTempoEnvelopeToAbjadAttachmentTempo._find_dynamic_change_indication(
                core_parameters.TempoPoint(120), core_parameters.TempoPoint(120)
            ),
            None,
        )
        self.assertEqual(
            abjad_converters.ComplexTempoEnvelopeToAbjadAttachmentTempo._find_dynamic_change_indication(
                core_parameters.TempoPoint(120),
                core_parameters.TempoPoint(60, reference=2),
            ),
            None,
        )

    def test_shall_write_metronome_mark(self):
        tempo_envelope_to_convert = expenvelope.Envelope.from_levels_and_durations(
            levels=[
                core_parameters.TempoPoint(bpm)
                for bpm in (120, 120, 110, 120, 110, 120, 110, 100)
            ],
            durations=[2, 2, 2, 2, 0, 2, 0],
        )
        self.assertEqual(
            abjad_converters.ComplexTempoEnvelopeToAbjadAttachmentTempo._shall_write_metronome_mark(
                tempo_envelope_to_convert,
                1,
                tempo_envelope_to_convert.levels[1],
                tempo_envelope_to_convert.levels,
            ),
            False,
        )
        self.assertEqual(
            abjad_converters.ComplexTempoEnvelopeToAbjadAttachmentTempo._shall_write_metronome_mark(
                tempo_envelope_to_convert,
                2,
                tempo_envelope_to_convert.levels[2],
                tempo_envelope_to_convert.levels,
            ),
            True,
        )
        self.assertEqual(
            abjad_converters.ComplexTempoEnvelopeToAbjadAttachmentTempo._shall_write_metronome_mark(
                tempo_envelope_to_convert,
                5,
                tempo_envelope_to_convert.levels[5],
                tempo_envelope_to_convert.levels,
            ),
            False,
        )
        self.assertEqual(
            abjad_converters.ComplexTempoEnvelopeToAbjadAttachmentTempo._shall_write_metronome_mark(
                tempo_envelope_to_convert,
                7,
                tempo_envelope_to_convert.levels[7],
                tempo_envelope_to_convert.levels,
            ),
            True,
        )

    def test_shall_stop_dynamic_change_indication(self):
        previous_tempo_attachments = (
            (0, abjad_parameters.Tempo(dynamic_change_indication="rit.")),
            (2, abjad_parameters.Tempo(dynamic_change_indication=None)),
        )
        self.assertEqual(
            abjad_converters.ComplexTempoEnvelopeToAbjadAttachmentTempo._shall_stop_dynamic_change_indication(
                previous_tempo_attachments
            ),
            False,
        )
        self.assertEqual(
            abjad_converters.ComplexTempoEnvelopeToAbjadAttachmentTempo._shall_stop_dynamic_change_indication(
                previous_tempo_attachments[:1]
            ),
            True,
        )

    def test_find_metronome_mark_values(self):
        self.assertEqual(
            abjad_converters.ComplexTempoEnvelopeToAbjadAttachmentTempo._find_metronome_mark_values(
                True,
                core_parameters.TempoPoint(
                    60, reference=2, textual_indication="ordinary"
                ),
                False,
            ),
            ((1, 2), 60, "ordinary"),
        )
        self.assertEqual(
            abjad_converters.ComplexTempoEnvelopeToAbjadAttachmentTempo._find_metronome_mark_values(
                True,
                core_parameters.TempoPoint(
                    120, reference=1, textual_indication="faster"
                ),
                False,
            ),
            ((1, 4), 120, "faster"),
        )
        self.assertEqual(
            abjad_converters.ComplexTempoEnvelopeToAbjadAttachmentTempo._find_metronome_mark_values(
                False,
                core_parameters.TempoPoint(
                    120, reference=1, textual_indication="faster"
                ),
                False,
            ),
            (None, None, None),
        )
        self.assertEqual(
            abjad_converters.ComplexTempoEnvelopeToAbjadAttachmentTempo._find_metronome_mark_values(
                False,
                core_parameters.TempoPoint(
                    120, reference=1, textual_indication="faster"
                ),
                True,
            ),
            (None, None, "a tempo"),
        )

    def test_process_tempo_event(self):
        tempo_envelope_to_convert = expenvelope.Envelope.from_levels_and_durations(
            levels=[
                core_parameters.TempoPoint(bpm)
                for bpm in (120, 120, 110, 120, 110, 120, 110, 100)
            ],
            durations=[2, 2, 2, 2, 0, 2, 0],
        )
        tempo_points = tempo_envelope_to_convert.levels
        tempo_attachments = (
            (
                0,
                abjad_parameters.Tempo(
                    reference_duration=(1, 4),
                    units_per_minute=120,
                    textual_indication=None,
                    dynamic_change_indication=None,
                    stop_dynamic_change_indicaton=False,
                    print_metronome_mark=True,
                ),
            ),
            (
                2,
                abjad_parameters.Tempo(
                    reference_duration=None,
                    units_per_minute=None,
                    textual_indication=None,
                    dynamic_change_indication="rit.",
                    stop_dynamic_change_indicaton=False,
                    print_metronome_mark=False,
                ),
            ),
            (
                4,
                abjad_parameters.Tempo(
                    reference_duration=(1, 4),
                    units_per_minute=110,
                    textual_indication=None,
                    dynamic_change_indication="acc.",
                    stop_dynamic_change_indicaton=True,
                    print_metronome_mark=True,
                ),
            ),
            (
                6,
                abjad_parameters.Tempo(
                    reference_duration=(1, 4),
                    units_per_minute=120,
                    textual_indication=None,
                    dynamic_change_indication="rit.",
                    stop_dynamic_change_indicaton=True,
                    print_metronome_mark=True,
                ),
            ),
            (
                8,
                abjad_parameters.Tempo(
                    reference_duration=None,
                    units_per_minute=None,
                    textual_indication="a tempo",
                    dynamic_change_indication="rit.",
                    stop_dynamic_change_indicaton=True,
                    print_metronome_mark=True,
                ),
            ),
        )

        for nth_tempo_point, nth_tempo_attachment in (
            (0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            (5, 4),
        ):
            tempo_point = tempo_points[nth_tempo_point]
            current_tempo_attachments = tempo_attachments[:nth_tempo_attachment]
            current_tempo_attachment = tempo_attachments[nth_tempo_attachment][1]
            self.assertEqual(
                abjad_converters.ComplexTempoEnvelopeToAbjadAttachmentTempo._process_tempo_event(
                    tempo_envelope_to_convert,
                    nth_tempo_point,
                    tempo_point,
                    tempo_points,
                    current_tempo_attachments,
                ),
                current_tempo_attachment,
            )


class SequentialEventToAbjadVoiceTest(unittest.TestCase):
    @staticmethod
    def _are_png_equal(path_to_png0: str, path_to_png1: str) -> bool:
        image0, image1 = (Image.open(path) for path in (path_to_png0, path_to_png1))
        difference = ImageChops.difference(image1, image0)
        return difference.getbbox() is None

    @staticmethod
    def _make_complex_sequential_event() -> core_events.SequentialEvent[
        music_events.NoteLike
    ]:
        complex_sequential_event = core_events.SequentialEvent(
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

        complex_sequential_event[
            0
        ].notation_indicator_collection.margin_markup.content = "Magic Instr"
        complex_sequential_event[
            2
        ].playing_indicator_collection.bartok_pizzicato.is_active = True
        complex_sequential_event[3].volume = "fff"
        complex_sequential_event[4].volume = "fff"
        complex_sequential_event[
            7
        ].playing_indicator_collection.fermata.fermata_type = "fermata"
        complex_sequential_event[9].notation_indicator_collection.ottava.n_octaves = -1
        complex_sequential_event[
            9
        ].playing_indicator_collection.string_contact_point.contact_point = "sul tasto"
        complex_sequential_event[
            11
        ].playing_indicator_collection.string_contact_point.contact_point = "sul tasto"
        complex_sequential_event[11].notation_indicator_collection.ottava.n_octaves = -2
        complex_sequential_event[
            12
        ].playing_indicator_collection.string_contact_point.contact_point = "pizzicato"
        return complex_sequential_event

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
        cls.complex_converter = abjad_converters.SequentialEventToAbjadVoice(
            abjad_converters.RMakersSequentialEventToQuantizedAbjadContainer(
                time_signature_sequence=[
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
                tempo_envelope=expenvelope.Envelope.from_levels_and_durations(
                    levels=(120, 120, 130, 130, 100), durations=(3, 2, 2.75, 0)
                ),
            )
        )
        cls.complex_sequential_event = (
            SequentialEventToAbjadVoiceTest._make_complex_sequential_event()
        )

    def test_convert(self):
        # TODO(improve readability of conversion method!)
        expected_abjad_voice = abjad.Voice(
            [
                abjad.score.Container("c'2. a'4"),
                abjad.score.Container([abjad.Tuplet(components="g'4 es'8 r8 r1")]),
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
            abjad.select(expected_abjad_voice).components(),
            abjad.select(converted_sequential_event).components(),
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

    def test_general_convert_with_lilypond_output(self):
        # core_eventsally an integration test (testing if the rendered png
        # is equal to the previously rendered and manually checked png)
        converted_sequential_event = self.complex_converter.convert(
            self.complex_sequential_event
        )
        tests_path = "tests/converters"
        png_file_to_compare_path = "{}/abjad_expected_png_output.png".format(tests_path)
        new_png_file_path = "{}/abjad_png_output.png".format(tests_path)
        lilypond_file = abjad.LilyPondFile()
        header_block = abjad.Block(name="header")
        header_block.tagline = abjad.Markup("---integration-test---")
        score_block = abjad.Block(name="score")
        score_block.items.append([abjad.Staff([converted_sequential_event])])
        lilypond_file.items.extend((header_block, score_block))
        abjad.persist.as_png(
            lilypond_file, png_file_path=new_png_file_path, remove_ly=True
        )

        self.assertTrue(
            SequentialEventToAbjadVoiceTest._are_png_equal(
                new_png_file_path, png_file_to_compare_path
            )
        )

        # remove test file
        os.remove(new_png_file_path)

    def test_tempo_range_conversion(self):
        # core_eventsally an integration test (testing if the rendered png
        # is equal to the previously rendered and manually checked png)
        # -> this tests, if the resulting notation prints tempo ranges

        tempo_envelope = expenvelope.Envelope.from_levels_and_durations(
            levels=[
                core_parameters.TempoPoint((30, 50), 2),
                core_parameters.TempoPoint((30, 50), 2),
            ],
            durations=[2],
        )
        converter = abjad_converters.SequentialEventToAbjadVoice(
            abjad_converters.RMakersSequentialEventToQuantizedAbjadContainer(
                tempo_envelope=tempo_envelope
            )
        )
        sequential_event_to_convert = core_events.SequentialEvent(
            [
                music_events.NoteLike("c", 1),
                music_events.NoteLike("c", 1),
                music_events.NoteLike("c", 1),
            ]
        )
        converted_sequential_event = converter.convert(sequential_event_to_convert)

        tests_path = "tests/converters"
        png_file_to_compare_path = (
            "{}/abjad_expected_png_output_for_tempo_range_test.png".format(tests_path)
        )
        new_png_file_path = "{}/abjad_png_output_for_tempo_range_test.png".format(
            tests_path
        )

        lilypond_file = abjad.LilyPondFile()
        header_block = abjad.Block(name="header")
        header_block.tagline = abjad.Markup("---integration-test---")
        score_block = abjad.Block(name="score")
        score_block.items.append([abjad.Staff([converted_sequential_event])])
        lilypond_file.items.extend((header_block, score_block))
        abjad.persist.as_png(
            lilypond_file, png_file_path=new_png_file_path, remove_ly=True
        )

        self.assertTrue(
            SequentialEventToAbjadVoiceTest._are_png_equal(
                new_png_file_path, png_file_to_compare_path
            )
        )

        # remove test file
        os.remove(new_png_file_path)

    def test_duration_line_notation(self):
        # core_eventsally an integration test (testing if the rendered png
        # is equal to the previously rendered and manually checked png)
        # -> this tests, if duration lines are printed in a correct manner

        converter = abjad_converters.SequentialEventToAbjadVoice(
            abjad_converters.NauertSequentialEventToDurationLineBasedQuantizedAbjadContainerConverter()
        )
        sequential_event_to_convert = core_events.SequentialEvent(
            [
                music_events.NoteLike([], 1),
                music_events.NoteLike("c", 0.125),
                music_events.NoteLike("d", 1),
                music_events.NoteLike([], 0.375),
                music_events.NoteLike("e", 0.25),
                music_events.NoteLike("d", 0.5),
                music_events.NoteLike("c", 0.75),
                music_events.NoteLike("a", 0.25),
            ]
        )
        converted_sequential_event = converter.convert(sequential_event_to_convert)

        tests_path = "tests/converters"
        png_file_to_compare_path = (
            "{}/abjad_expected_png_output_for_duration_line_test.png".format(tests_path)
        )
        new_png_file_path = "{}/abjad_png_output_for_duration_line_test.png".format(
            tests_path
        )

        lilypond_file = abjad.LilyPondFile()
        header_block = abjad.Block(name="header")
        header_block.tagline = abjad.Markup("---integration-test---")
        score_block = abjad.Block(name="score")
        score_block.items.append([abjad.Staff([converted_sequential_event])])
        lilypond_file.items.extend((header_block, score_block))
        abjad.persist.as_png(
            lilypond_file, png_file_path=new_png_file_path, remove_ly=True
        )

        self.assertTrue(
            SequentialEventToAbjadVoiceTest._are_png_equal(
                new_png_file_path, png_file_to_compare_path
            )
        )

        # remove test file
        os.remove(new_png_file_path)

    def test_grace_note_sequential_event_and_after_grace_note_sequential_event(self):
        # core_eventsally an integration test (testing if the rendered png
        # is equal to the previously rendered and manually checked png)
        # -> this tests, if the resulting notation prints grace notes and
        # after grace notes

        converter = abjad_converters.SequentialEventToAbjadVoice(
            abjad_converters.RMakersSequentialEventToQuantizedAbjadContainer()
        )
        sequential_event_to_convert = core_events.SequentialEvent(
            [
                music_events.NoteLike(
                    "c",
                    1,
                    grace_note_sequential_event=core_events.SequentialEvent(
                        [
                            music_events.NoteLike("d", 0.125),
                            music_events.NoteLike("e", 0.125),
                        ]
                    ),
                ),
                music_events.NoteLike(
                    "c",
                    1,
                    after_grace_note_sequential_event=core_events.SequentialEvent(
                        [
                            music_events.NoteLike("d", 0.125),
                            music_events.NoteLike("e", 0.125),
                            music_events.NoteLike("f", 0.125),
                        ]
                    ),
                ),
                music_events.NoteLike("c", 1),
                music_events.NoteLike(
                    "c",
                    1,
                    grace_note_sequential_event=core_events.SequentialEvent(
                        [
                            music_events.NoteLike("d", 0.125),
                            music_events.NoteLike("e", 0.125),
                        ]
                    ),
                ),
            ]
        )
        converted_sequential_event = converter.convert(sequential_event_to_convert)

        tests_path = "tests/converters"
        png_file_to_compare_path = "{}/abjad_expected_png_output_for_grace_note_sequential_event_test.png".format(
            tests_path
        )
        new_png_file_path = (
            "{}/abjad_png_output_for_grace_note_sequential_event_test.png".format(
                tests_path
            )
        )

        lilypond_file = abjad.LilyPondFile()
        header_block = abjad.Block(name="header")
        header_block.tagline = abjad.Markup("---integration-test---")
        score_block = abjad.Block(name="score")
        score_block.items.append(
            [abjad.Score([abjad.Staff([converted_sequential_event])])]
        )
        lilypond_file.items.extend((header_block, score_block))
        abjad.persist.as_png(
            lilypond_file, png_file_path=new_png_file_path, remove_ly=True
        )

        self.assertTrue(
            SequentialEventToAbjadVoiceTest._are_png_equal(
                new_png_file_path, png_file_to_compare_path
            )
        )

        # remove test file
        os.remove(new_png_file_path)

    def test_lyric_conversion(self):
        # Integration test!

        converter = abjad_converters.SequentialEventToAbjadVoice(
            abjad_converters.RMakersSequentialEventToQuantizedAbjadContainer()
        )
        sequential_event_to_convert = core_events.SequentialEvent(
            [
                music_events.NoteLike(
                    "c", 1, lyric=music_parameters.LanguageBasedLyric("helloDearTest")
                ),
                music_events.NoteLike(
                    "d",
                    fractions.Fraction(1, 8),
                    lyric=music_parameters.LanguageBasedLyric(""),
                ),
                music_events.NoteLike(
                    "e",
                    fractions.Fraction(1, 4),
                    lyric=music_parameters.LanguageBasedLyric("i"),
                ),
                music_events.NoteLike(
                    "e",
                    fractions.Fraction(3, 8),
                    lyric=music_parameters.LanguageBasedSyllable(False, "ho"),
                ),
                music_events.NoteLike(
                    "e",
                    fractions.Fraction(1, 4),
                    lyric=music_parameters.LanguageBasedSyllable(True, "pe"),
                ),
            ]
        )
        converted_sequential_event = converter.convert(sequential_event_to_convert)

        tests_path = "tests/converters"
        png_file_to_compare_path = (
            "{}/abjad_expected_png_output_for_lyric_test.png".format(tests_path)
        )
        new_png_file_path = "{}/abjad_png_output_for_lyric_test.png".format(tests_path)

        lilypond_file = abjad.LilyPondFile()
        header_block = abjad.Block(name="header")
        header_block.tagline = abjad.Markup("---integration-test---")
        score_block = abjad.Block(name="score")
        score_block.items.append(
            [abjad.Score([abjad.Staff([converted_sequential_event])])]
        )
        lilypond_file.items.extend((header_block, score_block))
        abjad.persist.as_png(
            lilypond_file, png_file_path=new_png_file_path, remove_ly=True
        )

        self.assertTrue(
            SequentialEventToAbjadVoiceTest._are_png_equal(
                new_png_file_path, png_file_to_compare_path
            )
        )

        # remove test file
        os.remove(new_png_file_path)


class NestedComplexEventToAbjadContainerTest(unittest.TestCase):
    def test_nested_conversion(self):
        # core_eventsally an integration test (testing if the rendered png
        # is equal to the previously rendered and manually checked png)

        nested_score = core_events.TaggedSimultaneousEvent(
            [
                core_events.TaggedSimultaneousEvent(
                    [
                        core_events.SequentialEvent(
                            [
                                music_events.NoteLike(pitch, duration)
                                for pitch, duration in zip(
                                    "c d e f g a b".split(" "), (1 / 4,) * 7
                                )
                            ]
                        ),
                        core_events.SequentialEvent(
                            [
                                music_events.NoteLike(pitch, duration)
                                for pitch, duration in [
                                    [music_parameters.WesternPitch("c", 3), 1 / 2]
                                ]
                                * 4
                            ]
                        ),
                    ],
                    tag="Piano",
                ),
                core_events.TaggedSimultaneousEvent(
                    [
                        core_events.SequentialEvent(
                            [
                                music_events.NoteLike(pitch, duration)
                                for pitch, duration in [
                                    [music_parameters.WesternPitch("es", 5), 1 / 2]
                                ]
                                * 4
                            ]
                        ),
                        core_events.SequentialEvent(
                            [
                                music_events.NoteLike(pitch, duration)
                                for pitch, duration in [
                                    [music_parameters.WesternPitch("b", 3), 1 / 2]
                                ]
                                * 4
                            ]
                        ),
                    ],
                    tag="Violin",
                ),
            ],
            tag="Integrating duo",
        )

        converter = abjad_converters.NestedComplexEventToAbjadContainer(
            abjad_converters.TagBasedNestedComplexEventToComplexEventToAbjadContainers(
                {
                    "Piano": abjad_converters.NestedComplexEventToAbjadContainer(
                        abjad_converters.CycleBasedNestedComplexEventToComplexEventToAbjadContainers(
                            [
                                abjad_converters.SequentialEventToAbjadVoice(
                                    abjad_converters.RMakersSequentialEventToQuantizedAbjadContainer()
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

        abjad_score = converter.convert(nested_score)

        # check if abjad container type is correct
        self.assertEqual(type(abjad_score), abjad.Score)

        # check if abjad container name is correct
        self.assertEqual(abjad_score.name, "Integrating duo")

        tests_path = "tests/converters"
        png_file_to_compare_path = (
            "{}/abjad_expected_png_output_for_nested_complex_event_test.png".format(
                tests_path
            )
        )
        new_png_file_path = (
            "{}/abjad_png_output_for_nested_complex_event_test.png".format(tests_path)
        )

        lilypond_file = abjad.LilyPondFile()
        header_block = abjad.Block(name="header")
        header_block.tagline = abjad.Markup("---integration-test---")
        lilypond_file.items.extend((header_block, abjad_score))
        abjad.persist.as_png(
            lilypond_file, png_file_path=new_png_file_path, remove_ly=True
        )

        self.assertTrue(
            SequentialEventToAbjadVoiceTest._are_png_equal(
                new_png_file_path, png_file_to_compare_path
            )
        )

        # remove test file
        os.remove(new_png_file_path)


if __name__ == "__main__":
    unittest.main()
