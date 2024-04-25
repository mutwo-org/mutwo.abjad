"""Test conversion of mutwo to abjad parameters"""

import fractions
import unittest

import abjad  # type: ignore

from mutwo import abjad_converters
from mutwo import abjad_parameters
from mutwo import abjad_utilities
from mutwo import core_events
from mutwo import core_parameters
from mutwo import core_utilities
from mutwo import music_parameters


class MutwoPitchToAbjadPitchTest(unittest.TestCase):
    def test_convert(self):
        converter = abjad_converters.MutwoPitchToAbjadPitch()
        for mutwo_pitch, expected_abjad_pitch in (
            (
                music_parameters.WesternPitch("ds", 4),
                abjad.NamedPitch("ds'"),
            ),
            (
                music_parameters.WesternPitch("gf", 5),
                abjad.NamedPitch("gf''"),
            ),
            (
                music_parameters.WesternPitch("gts", 5),
                abjad.NamedPitch("g''"),
            ),
            (
                music_parameters.WesternPitch("dqs", 4),
                abjad.NamedPitch("dqs'"),
            ),
            (
                music_parameters.JustIntonationPitch("3/2", concert_pitch=262),
                abjad.NumberedPitch(7),
            ),
            (
                music_parameters.JustIntonationPitch("3/4", concert_pitch=262),
                abjad.NumberedPitch(-5),
            ),
            (
                music_parameters.JustIntonationPitch("5/4", concert_pitch=262),
                abjad.NumberedPitch(4),
            ),
        ):
            self.assertEqual(
                converter.convert(mutwo_pitch).number, expected_abjad_pitch.number
            )


class MutwoPitchToHEJIAbjadPitchTest(unittest.TestCase):
    @abjad_utilities.run_if_ekmelily_available
    def test_convert(self):
        converter = abjad_converters.MutwoPitchToHEJIAbjadPitch(reference_pitch="c")
        for mutwo_pitch, expected_abjad_pitch in (
            (music_parameters.JustIntonationPitch("1/1"), abjad.NamedPitch("c'")),
            (music_parameters.JustIntonationPitch("3/2"), abjad.NamedPitch("g'")),
        ):
            self.assertEqual(
                abjad.lilypond(converter.convert(mutwo_pitch)),
                abjad.lilypond(expected_abjad_pitch),
            )
        for mutwo_pitch, expected_lilypond_string in (
            # JustIntonationPitch conversion
            (music_parameters.JustIntonationPitch("5/4"), "eoaa'"),
            (music_parameters.JustIntonationPitch("7/4"), "bfoba'"),
            (music_parameters.JustIntonationPitch("7/6"), "efoba'"),
            (music_parameters.JustIntonationPitch("12/7"), "auba'"),
            (music_parameters.JustIntonationPitch("9/8"), "d'"),
            (music_parameters.JustIntonationPitch("9/16"), "d"),
            (music_parameters.JustIntonationPitch("9/4"), "d''"),
            (music_parameters.JustIntonationPitch("32/33"), "cuca'"),
            (music_parameters.JustIntonationPitch("49/50"), "dffuabobb'"),
            # Any other pitch object conversion
            (music_parameters.WesternPitch("cqs"), "cs'"),
            (music_parameters.WesternPitch("cts"), "c'"),
            (music_parameters.WesternPitch("cs"), "cs'"),
            (music_parameters.DirectPitch(440), "a'"),
            (music_parameters.DirectPitch(445), "a'"),
        ):
            self.assertEqual(
                abjad.lilypond(converter.convert(mutwo_pitch)),
                expected_lilypond_string,
            )


class MutwoVolumeToAbjadAttachmentDynamicTest(unittest.TestCase):
    def test_convert(self):
        converter = abjad_converters.MutwoVolumeToAbjadAttachmentDynamic()
        d = abjad_parameters.Dynamic
        wv, dv = music_parameters.WesternVolume, music_parameters.DirectVolume
        for mutwo_volume, expected_abjad_parameter in (
            (wv("mf"), d(dynamic_indicator="mf")),
            (wv("fff"), d(dynamic_indicator="fff")),
            (dv(-6), d(dynamic_indicator=wv.from_decibel(-6).name)),
        ):
            self.assertEqual(
                converter.convert(mutwo_volume),
                expected_abjad_parameter,
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


class ComplexTempoToAbjadAttachmentTempoTest(unittest.TestCase):
    def test_convert_tempo_tuple(self):
        self.assertEqual(
            abjad_converters.ComplexTempoToAbjadAttachmentTempo._convert_tempo_tuple(
                (60, 120, core_parameters.WesternTempo(120, reference=4))
            ),
            (
                core_parameters.DirectTempo(60),
                core_parameters.DirectTempo(120),
                core_parameters.WesternTempo(120, reference=4),
            ),
        )

    def test_find_dynamic_change_indication(self):
        for tempo_tuple, expected_dynamic_change_indication in (
            (
                (
                    core_parameters.DirectTempo(120),
                    core_parameters.DirectTempo(130),
                ),
                "acc.",
            ),
            (
                (
                    core_parameters.DirectTempo(120),
                    core_parameters.DirectTempo(110),
                ),
                "rit.",
            ),
            (
                (
                    core_parameters.DirectTempo(120),
                    core_parameters.DirectTempo(120),
                ),
                None,
            ),
            (
                (
                    core_parameters.DirectTempo(120),
                    core_parameters.WesternTempo(60, reference=2),
                ),
                None,
            ),
        ):
            self.assertEqual(
                abjad_converters.ComplexTempoToAbjadAttachmentTempo._find_dynamic_change_indication(
                    *tempo_tuple
                ),
                expected_dynamic_change_indication,
            )

    def test_shall_write_metronome_mark(self):
        duration_list = [2, 2, 2, 2, 0, 2, 0]
        absolute_duration_list = list(
            core_utilities.accumulate_from_zero(duration_list)
        )
        value_list = [
            core_parameters.DirectTempo(bpm)
            for bpm in (120, 120, 110, 120, 110, 120, 110, 100)
        ]
        tempo_to_convert = core_parameters.FlexTempo(
            tuple(zip(absolute_duration_list, value_list))
        )
        for tempo_index, shall_write_metronome_mark in (
            (1, False),
            (2, True),
            (5, False),
            (7, True),
        ):
            self.assertEqual(
                abjad_converters.ComplexTempoToAbjadAttachmentTempo._shall_write_metronome_mark(
                    tempo_to_convert,
                    tempo_index,
                    tempo_to_convert.parameter_tuple[tempo_index],
                    tempo_to_convert.parameter_tuple,
                ),
                shall_write_metronome_mark,
            )

    def test_shall_stop_dynamic_change_indication(self):
        previous_tempo_attachment_tuple = (
            (0, abjad_parameters.Tempo(dynamic_change_indication="rit.")),
            (2, abjad_parameters.Tempo(dynamic_change_indication=None)),
        )
        for (
            local_previous_tempo_attachment_tuple,
            shall_stop_dynamic_change_indication,
        ) in (
            (previous_tempo_attachment_tuple, False),
            (previous_tempo_attachment_tuple[:1], True),
        ):
            self.assertEqual(
                abjad_converters.ComplexTempoToAbjadAttachmentTempo._shall_stop_dynamic_change_indication(
                    local_previous_tempo_attachment_tuple
                ),
                shall_stop_dynamic_change_indication,
            )

    def test_find_metronome_mark_values(self):
        for (
            write_metronome_mark,
            tempo,
            stop_dynamic_change_indicaton,
            expected_metronome_mark_values,
        ) in (
            (
                True,
                core_parameters.WesternTempo(
                    60,
                    reference=fractions.Fraction(1, 2),
                    textual_indication="ordinary",
                ),
                False,
                ((1, 2), 60, "ordinary"),
            ),
            (
                True,
                core_parameters.WesternTempo(
                    120, reference=fractions.Fraction(1, 4), textual_indication="faster"
                ),
                False,
                ((1, 4), 120, "faster"),
            ),
            (
                False,
                core_parameters.WesternTempo(
                    120, reference=fractions.Fraction(1, 4), textual_indication="faster"
                ),
                False,
                (None, None, None),
            ),
            (
                False,
                core_parameters.WesternTempo(
                    120, reference=fractions.Fraction(1, 4), textual_indication="faster"
                ),
                True,
                (None, None, "a tempo"),
            ),
        ):
            self.assertEqual(
                abjad_converters.ComplexTempoToAbjadAttachmentTempo._find_metronome_mark_values(
                    write_metronome_mark,
                    tempo,
                    stop_dynamic_change_indicaton,
                ),
                expected_metronome_mark_values,
            )

    def test_process_tempo_chronon(self):
        duration_list = [2, 2, 2, 2, 0, 2, 0]
        absolute_duration_list = list(
            core_utilities.accumulate_from_zero(duration_list)
        )
        value_list = [
            core_parameters.WesternTempo(bpm)
            for bpm in (120, 120, 110, 120, 110, 120, 110, 100)
        ]
        tempo_to_convert = core_parameters.FlexTempo(
            tuple(zip(absolute_duration_list, value_list))
        )
        tempo_tuple = tempo_to_convert.parameter_tuple
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

        for tempo_index, tempo_attachment_index in (
            (0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            (5, 4),
        ):
            tempo = tempo_tuple[tempo_index]
            current_tempo_attachments = tempo_attachments[:tempo_attachment_index]
            current_tempo_attachment = tempo_attachments[tempo_attachment_index][1]
            self.assertEqual(
                abjad_converters.ComplexTempoToAbjadAttachmentTempo._process_tempo_chronon(
                    tempo_to_convert,
                    tempo_index,
                    tempo,
                    tempo_tuple,
                    current_tempo_attachments,
                ),
                current_tempo_attachment,
            )
