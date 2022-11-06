"""Build Abjad attachments from Mutwo data.
"""

import dataclasses
import inspect
import typing
import warnings

import abjad  # type: ignore

from mutwo import abjad_parameters
from mutwo import music_parameters

LeafOrLeafSequence = typing.Union[abjad.Leaf, typing.Sequence[abjad.Leaf]]


class Arpeggio(music_parameters.Arpeggio, abjad_parameters.abc.BangFirstAttachment):
    _string_to_direction = {
        "up": abjad.enums.UP,
        "down": abjad.enums.DOWN,
        "center": abjad.enums.CENTER,
        "^": abjad.enums.UP,
        "_": abjad.enums.DOWN,
    }

    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        direction = self.direction
        if direction in self._string_to_direction:
            direction = self._string_to_direction[direction]
        abjad.attach(abjad.Arpeggio(direction=direction), leaf)
        return leaf


class Articulation(
    music_parameters.Articulation, abjad_parameters.abc.BangEachAttachment
):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(abjad.Articulation(self.name), leaf)
        return leaf


class Trill(music_parameters.Trill, abjad_parameters.abc.BangFirstAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(abjad.Articulation("trill"), leaf)
        return leaf


class Cue(music_parameters.Cue, abjad_parameters.abc.BangFirstAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.Markup(string=rf"\markup \rounded-box {{ {self.nth_cue} }}"),
            leaf,
            direction=abjad.enums.UP,
        )
        return leaf


class WoodwindFingering(
    music_parameters.WoodwindFingering, abjad_parameters.abc.BangFirstAttachment
):
    fingering_size = 0.7

    @staticmethod
    def _tuple_to_scheme_list(tuple_to_convert: tuple[str, ...]) -> str:
        return f"({' '.join(tuple_to_convert)})"

    def _get_markup_content(self) -> str:
        # \\override #'(graphical . #f)
        return f"""
\\override #'(size . {self.fingering_size})
{{
    \\woodwind-diagram
    #'{self.instrument}
    #'((cc . {self._tuple_to_scheme_list(self.cc)})
       (lh . {self._tuple_to_scheme_list(self.left_hand)})
       (rh . {self._tuple_to_scheme_list(self.right_hand)}))
}}"""

    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        fingering = abjad.LilyPondLiteral(
            f"^\\markup {self._get_markup_content()}", site="after"
        )
        abjad.attach(fingering, leaf)
        return leaf


class Tremolo(music_parameters.Tremolo, abjad_parameters.abc.BangEachAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.StemTremolo(self.n_flags * (2**leaf.written_duration.flag_count)),
            leaf,
        )
        return leaf


class ArtificalHarmonic(
    music_parameters.ArtificalHarmonic, abjad_parameters.abc.BangEachAttachment
):
    @staticmethod
    def _change_note_head_style(leaf: abjad.Chord) -> None:
        abjad.tweak(leaf.note_heads[1]).NoteHead.style = "#'harmonic"

    @staticmethod
    def _convert_and_test_leaf(leaf: abjad.Leaf) -> tuple[abjad.Leaf, bool]:
        # return True if artifical_harmonic can be attached and False if
        # artifical harmonic can't be attached

        if isinstance(leaf, abjad.Chord):
            try:
                assert len(leaf.note_heads) == 1
            except AssertionError:
                message = (
                    "Can't attach artifical harmonic on chord with more or less"
                    " than one pitch!"
                )
                warnings.warn(message)
                return leaf, False

            return leaf, True

        elif isinstance(leaf, abjad.Note):
            new_abjad_leaf = abjad.Chord(
                [leaf.written_pitch],
                leaf.written_duration,
            )
            for indicator in abjad.get.indicators(leaf):
                if type(indicator) != dict:
                    abjad.attach(indicator, new_abjad_leaf)

            return new_abjad_leaf, True

        else:
            message = "Can't attach artifical harmonic on abjad leaf '{}' of type '{}'!".format(
                leaf, type(leaf)
            )
            warnings.warn(message)
            return leaf, False

    def _get_second_pitch(self, abjad_pitch: abjad.Pitch) -> abjad.Pitch:
        return abjad_pitch + self.n_semitones

    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        leaf, is_attachable = ArtificalHarmonic._convert_and_test_leaf(leaf)
        if is_attachable:
            first_pitch = leaf.note_heads[0].written_pitch
            second_pitch = self._get_second_pitch(first_pitch)
            leaf.written_pitches = abjad.PitchSegment([first_pitch, second_pitch])
            ArtificalHarmonic._change_note_head_style(leaf)
        return leaf


class PreciseNaturalHarmonic(
    music_parameters.PreciseNaturalHarmonic, abjad_parameters.abc.BangEachAttachment
):
    @staticmethod
    def _convert_leaf(leaf: abjad.Leaf) -> tuple[abjad.Leaf, bool]:
        if isinstance(leaf, abjad.Chord):
            return leaf

        else:
            new_abjad_leaf = abjad.Chord(
                "c",
                leaf.written_duration,
            )
            for indicator in abjad.get.indicators(leaf):
                if type(indicator) != dict:
                    abjad.attach(indicator, new_abjad_leaf)

            return new_abjad_leaf

    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        if isinstance(leaf, (abjad.Chord, abjad.Note)):
            leaf = PreciseNaturalHarmonic._convert_leaf(leaf)
            leaf.written_pitches = abjad.PitchSegment(
                [
                    self.string_pitch,
                    abjad.NamedPitch(
                        self.string_pitch.name,
                        octave=self.string_pitch.octave.number + 1,
                    ),
                ]
            )
            leaf.note_heads[1]._written_pitch = self.played_pitch
            if self.harmonic_note_head_style:
                ArtificalHarmonic._change_note_head_style(leaf)
            if self.parenthesize_lower_note_head:
                leaf.note_heads[0].is_parenthesized = True

        return leaf


class StringContactPoint(
    music_parameters.StringContactPoint, abjad_parameters.abc.ToggleAttachment
):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Extend abjad with custom string contact points
        class StringContactPoint(abjad.StringContactPoint):
            _contact_point = abjad.StringContactPoint._contact_points + tuple(
                abjad_parameters.configurations.CUSTOM_STRING_CONTACT_POINT_DICT.keys()
            )
            _contact_point_abbreviations = dict(
                abjad.StringContactPoint._contact_point_abbreviations,
                **abjad_parameters.configurations.CUSTOM_STRING_CONTACT_POINT_DICT,
            )

        self._string_contact_point_class = StringContactPoint
        self._abbreviation_to_string_contact_point = {
            abbreviation: full_name
            for full_name, abbreviation in StringContactPoint._contact_point_abbreviations.items()
        }

    def _attach_string_contact_point(
        self,
        leaf: abjad.Leaf,
        previous_attachment: typing.Optional["abjad_parameters.abc.AbjadAttachment"],
        string_contact_point_markup_string: str,
    ):
        if previous_attachment:
            if previous_attachment.contact_point == "pizzicato":  # type: ignore
                string_contact_point_markup_string = (
                    rf"\caps {{ \arco {string_contact_point_markup_string} }}"
                )

        final_markup = abjad.Markup(
            rf"\markup \fontsize #-2.4 {{ {string_contact_point_markup_string} }}",
        )
        abjad.attach(
            final_markup,
            leaf,
            direction=abjad.enums.UP,
        )

    def process_leaf(
        self,
        leaf: abjad.Leaf,
        previous_attachment: typing.Optional["abjad_parameters.abc.AbjadAttachment"],
    ) -> LeafOrLeafSequence:
        contact_point = self.contact_point
        if contact_point in self._abbreviation_to_string_contact_point:
            contact_point = self._abbreviation_to_string_contact_point[contact_point]
        try:
            string_contact_point_markup_string = self._string_contact_point_class(
                contact_point
            ).markup_string
        except AssertionError:
            warnings.warn(
                f"Can't find contact point '{self.contact_point}' "
                f"in '{self._string_contact_point_class._contact_point_abbreviations}'!"
            )
        else:
            self._attach_string_contact_point(
                leaf, previous_attachment, string_contact_point_markup_string
            )
        return leaf

    def process_leaf_tuple(
        self,
        leaf_tuple: tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional["abjad_parameters.abc.AbjadAttachment"],
    ) -> tuple[abjad.Leaf, ...]:
        # don't attach ordinario at start (this is the default playing technique)
        if previous_attachment is not None or self.contact_point != "ordinario":
            return super().process_leaf_tuple(leaf_tuple, previous_attachment)
        else:
            return leaf_tuple


class Pedal(music_parameters.Pedal, abjad_parameters.abc.ToggleAttachment):
    def process_leaf(
        self,
        leaf: abjad.Leaf,
        previous_attachment: typing.Optional["abjad_parameters.abc.AbjadAttachment"],
    ) -> LeafOrLeafSequence:
        if self.pedal_activity:
            pedal_class = abjad.StartPianoPedal
        else:
            pedal_class = abjad.StopPianoPedal

        abjad.attach(pedal_class(self.pedal_type), leaf)
        return leaf

    def process_leaf_tuple(
        self,
        leaf_tuple: tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional["abjad_parameters.abc.AbjadAttachment"],
    ) -> tuple[abjad.Leaf, ...]:
        # don't attach pedal down at start
        if previous_attachment is not None or self.is_active:
            return super().process_leaf_tuple(leaf_tuple, previous_attachment)
        else:
            return leaf_tuple


class Hairpin(music_parameters.Hairpin, abjad_parameters.abc.ToggleAttachment):
    niente_literal = abjad.LilyPondLiteral(r"\once \override Hairpin.circled-tip = ##t")

    def process_leaf(
        self,
        leaf: abjad.Leaf,
        _: typing.Optional["abjad_parameters.abc.AbjadAttachment"],
    ) -> LeafOrLeafSequence:
        if self.symbol == "!":
            abjad.attach(
                abjad.StopHairpin(),
                leaf,
            )
        else:
            if self.niente:
                abjad.attach(self.niente_literal, leaf)
            abjad.attach(
                abjad.StartHairpin(self.symbol),
                leaf,
            )
        return leaf

    def _process_espressivo(
        self,
        leaf_tuple: tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional[abjad_parameters.abc.AbjadAttachment],
    ) -> tuple[abjad.Leaf, ...]:
        leaf_count = len(leaf_tuple)
        if leaf_count >= 2:
            crescendo_leaf = leaf_tuple[0]
            if self.niente:
                abjad.attach(self.niente_literal, crescendo_leaf)
            abjad.attach(abjad.StartHairpin("<"), crescendo_leaf)
            decrescendo_leaf = leaf_tuple[int(len(leaf_tuple) // 2)]
            if self.niente:
                abjad.attach(self.niente_literal, decrescendo_leaf)
            abjad.attach(abjad.StartHairpin(">"), decrescendo_leaf)

        elif leaf_count == 1:
            abjad.attach(abjad.Articulation("espressivo"), leaf_tuple[0])

        return leaf_tuple

    def process_leaf_tuple(
        self,
        leaf_tuple: tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional[abjad_parameters.abc.AbjadAttachment],
    ) -> tuple[abjad.Leaf, ...]:
        if self.symbol == "<>":
            return self._process_espressivo(leaf_tuple, previous_attachment)
        else:
            return super().process_leaf_tuple(leaf_tuple, previous_attachment)


class BartokPizzicato(
    music_parameters.abc.ExplicitPlayingIndicator,
    abjad_parameters.abc.BangFirstAttachment,
):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.LilyPondLiteral("\\snappizzicato", site="after"),
            leaf,
        )
        return leaf


class BreathMark(
    music_parameters.abc.ExplicitPlayingIndicator,
    abjad_parameters.abc.BangFirstAttachment,
):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.LilyPondLiteral("\\breathe", site="before"),
            leaf,
        )
        return leaf


class Fermata(music_parameters.Fermata, abjad_parameters.abc.BangFirstAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.Fermata(self.fermata_type),
            leaf,
        )
        return leaf


class NaturalHarmonic(
    music_parameters.abc.ExplicitPlayingIndicator,
    abjad_parameters.abc.BangFirstAttachment,
):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.LilyPondLiteral("\\flageolet", directed="up", site="after"),
            leaf,
        )

        return leaf


class Prall(
    music_parameters.abc.ExplicitPlayingIndicator,
    abjad_parameters.abc.BangFirstAttachment,
):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.LilyPondLiteral("^\\prall", site="after"),
            leaf,
        )
        return leaf


class Tie(
    music_parameters.abc.ExplicitPlayingIndicator,
    abjad_parameters.abc.BangLastAttachment,
):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        if isinstance(leaf, (abjad.Chord, abjad.Note)):
            abjad.attach(
                abjad.Tie(),
                leaf,
            )
        return leaf


class DurationLineTriller(
    music_parameters.abc.ExplicitPlayingIndicator,
    abjad_parameters.abc.BangEachAttachment,
):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        if isinstance(leaf, (abjad.Chord, abjad.Note)):
            abjad.attach(
                abjad.LilyPondLiteral("\\once \\override DurationLine.style = #'trill"),
                leaf,
            )
        return leaf


class DurationLineDashed(
    music_parameters.abc.ExplicitPlayingIndicator,
    abjad_parameters.abc.BangEachAttachment,
):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        if isinstance(leaf, (abjad.Chord, abjad.Note)):
            abjad.attach(
                abjad.LilyPondLiteral(
                    "\\once \\override DurationLine.style = #'dashed-line"
                ),
                leaf,
            )
        return leaf


class Glissando(
    music_parameters.abc.ExplicitPlayingIndicator,
    abjad_parameters.abc.BangLastAttachment,
):
    thickness = 3
    minimum_length = 5

    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.LilyPondLiteral(
                "\\override Glissando.thickness = #'{}".format(self.thickness)
            ),
            leaf,
        )
        abjad.attach(
            abjad.LilyPondLiteral(
                "\\override Glissando.minimum-length = #{}".format(self.minimum_length)
            ),
            leaf,
        )
        abjad.attach(
            abjad.LilyPondLiteral("\\override Glissando.breakable = ##t"),
            leaf,
        )
        abjad.attach(
            abjad.LilyPondLiteral("\\override Glissando.after-line-breaking = ##t"),
            leaf,
        )
        # Prevent duration line from getting printed when we print a glissando
        abjad.attach(
            abjad.LilyPondLiteral("\\once \\override DurationLine.style = #'none"), leaf
        )
        command = "\\override "
        command += "Glissando.springs-and-rods = #ly:spanner::set-spacing-rods"
        abjad.attach(abjad.LilyPondLiteral(command), leaf)
        abjad.attach(
            abjad.Glissando(allow_ties=True),
            leaf,
        )
        return leaf


class BendAfter(music_parameters.BendAfter, abjad_parameters.abc.BangLastAttachment):
    def _attach_bend_after_to_note(self, note: abjad.Note):
        abjad.attach(
            abjad.LilyPondLiteral(
                "\\once \\override BendAfter.thickness = #'{}".format(self.thickness)
            ),
            note,
        )
        abjad.attach(
            abjad.LilyPondLiteral(
                f"\\once \\override BendAfter.minimum-length = #{self.minimum_length}"
            ),
            note,
        )
        abjad.attach(
            abjad.LilyPondLiteral("\\once \\override DurationLine.style = #'none"), note
        )
        abjad.attach(abjad.BendAfter(bend_amount=self.bend_amount), note)

    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        if isinstance(leaf, abjad.Chord):
            indicator_list = abjad.get.indicators(leaf)
            container = abjad.Container([], simultaneous=True)
            for note_head in leaf.note_heads:
                note = abjad.Note("c", leaf.written_duration)
                note.note_head._written_pitch = note_head.written_pitch
                self._attach_bend_after_to_note(note)
                for indicator in indicator_list:
                    abjad.attach(indicator, note)
                voice = abjad.Voice([note])
                container.append(voice)

            return container

        elif isinstance(leaf, abjad.Note):
            self._attach_bend_after_to_note(leaf)

        return leaf


class LaissezVibrer(
    music_parameters.abc.ExplicitPlayingIndicator,
    abjad_parameters.abc.BangLastAttachment,
):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.LaissezVibrer(),
            leaf,
        )
        return leaf


class BarLine(music_parameters.BarLine, abjad_parameters.abc.BangLastAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.BarLine(self.abbreviation),
            leaf,
        )
        return leaf


class Clef(music_parameters.Clef, abjad_parameters.abc.BangFirstAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.Clef(self.name),
            leaf,
        )
        return leaf


class Ottava(music_parameters.Ottava, abjad_parameters.abc.ToggleAttachment):
    def process_leaf(
        self,
        leaf: abjad.Leaf,
        previous_attachment: typing.Optional["abjad_parameters.abc.AbjadAttachment"],
    ) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.Ottava(self.n_octaves, site="before"),
            leaf,
        )
        return leaf

    def process_leaf_tuple(
        self,
        leaf_tuple: tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional["abjad_parameters.abc.AbjadAttachment"],
    ) -> tuple[abjad.Leaf, ...]:
        # don't attach ottava = 0 at start (this is the default notation)
        if previous_attachment is not None or self.n_octaves != 0:
            return super().process_leaf_tuple(leaf_tuple, previous_attachment)
        else:
            return leaf_tuple


class Markup(music_parameters.Markup, abjad_parameters.abc.BangFirstAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(abjad.Markup(self.content), leaf, direction=self.direction)
        return leaf


class RehearsalMark(
    music_parameters.RehearsalMark, abjad_parameters.abc.BangFirstAttachment
):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.RehearsalMark(markup=self.markup),
            leaf,
        )
        return leaf


class MarginMarkup(
    music_parameters.MarginMarkup, abjad_parameters.abc.BangFirstAttachment
):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        command = "\\set {}.instrumentName = \\markup ".format(self.context)
        command += "{ " + self.content + " }"  # type: ignore
        abjad.attach(
            abjad.LilyPondLiteral(command),
            leaf,
        )
        return leaf


class Ornamentation(
    music_parameters.Ornamentation, abjad_parameters.abc.BangFirstAttachment
):
    _direction_to_ornamentation_command = {
        "up": """
    #'((moveto 0 0)
      (lineto 0.5 0)
      (curveto 0.5 0 1.5 1.75 2.5 0)
      (lineto 3.5 0))""",
        "down": """
    #'((moveto 0 0)
      (lineto 0.5 0)
      (curveto 0.5 0 1.5 -1.75 2.5 0)
      (lineto 3.5 0))""",
    }

    def _make_markup(self) -> abjad.Markup:
        return abjad.Markup(
            r"\vspace #-0.25 { \fontsize #-4 { "
            rf"\rounded-box {{ {self.n_times} "
            r"\hspace #-0.4 \path 0.25 "
            f"{self._direction_to_ornamentation_command[self.direction]}"
            "}}}"
        )

    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            self._make_markup(),
            leaf,
            direction=abjad.enums.UP,
        )
        return leaf


@dataclasses.dataclass()
class Dynamic(abjad_parameters.abc.ToggleAttachment):
    dynamic_indicator: str = "mf"  # TODO(for future usage add typing.Literal)

    @classmethod
    def from_indicator_collection(
        cls, indicator_collection: music_parameters.abc.IndicatorCollection
    ) -> typing.Optional["abjad_parameters.abc.AbjadAttachment"]:
        """Always return None.

        Dynamic can't be initialised from IndicatorCollection.
        """
        return None

    @property
    def is_active(self) -> bool:
        return True

    def process_leaf(
        self,
        leaf: abjad.Leaf,
        previous_attachment: typing.Optional["abjad_parameters.abc.AbjadAttachment"],
    ) -> LeafOrLeafSequence:
        abjad.attach(abjad.Dynamic(self.dynamic_indicator), leaf)
        return leaf


@dataclasses.dataclass()
class Tempo(abjad_parameters.abc.BangFirstAttachment):
    reference_duration: typing.Optional[tuple[int, int]] = (1, 4)
    units_per_minute: typing.Union[int, tuple[int, int], None] = 60
    textual_indication: typing.Optional[str] = None
    # TODO(for future usage add typing.Literal['rit.', 'acc.'])
    dynamic_change_indication: typing.Optional[str] = None
    stop_dynamic_change_indicaton: bool = False
    print_metronome_mark: bool = True

    @classmethod
    def from_indicator_collection(
        cls, indicator_collection: music_parameters.abc.IndicatorCollection
    ) -> typing.Optional["abjad_parameters.abc.AbjadAttachment"]:
        """Always return None.

        Tempo can't be initialised from IndicatorCollection.
        """
        return None

    @property
    def is_active(self) -> bool:
        return True

    def _attach_metronome_mark(self, leaf: abjad.Leaf) -> None:
        if self.print_metronome_mark:
            abjad.attach(
                abjad.MetronomeMark(
                    reference_duration=self.reference_duration,
                    units_per_minute=self.units_per_minute,
                    textual_indication=self.textual_indication,
                ),
                leaf,
            )

    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        self._attach_metronome_mark(leaf)

        if self.dynamic_change_indication is not None:
            dynamic_change_indication = abjad.StartTextSpan(
                left_text=abjad.Markup(self.dynamic_change_indication)
            )
            abjad.attach(dynamic_change_indication, leaf)

        return leaf


class DynamicChangeIndicationStop(abjad_parameters.abc.BangFirstAttachment):
    @classmethod
    def from_indicator_collection(
        cls, indicator_collection: music_parameters.abc.IndicatorCollection
    ) -> typing.Optional["abjad_parameters.abc.AbjadAttachment"]:
        """Always return None.

        DynamicChangeIndicationStop can't be initialised from IndicatorCollection.
        """
        return None

    @property
    def is_active(self) -> bool:
        return True

    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(abjad.StopTextSpan(), leaf)
        return leaf


class GraceNoteSequentialEvent(abjad_parameters.abc.BangFirstAttachment):
    def __init__(self, grace_note_sequential_event: abjad.BeforeGraceContainer):
        self._grace_note_sequential_event = grace_note_sequential_event

    @classmethod
    def from_indicator_collection(
        cls, indicator_collection: music_parameters.abc.IndicatorCollection
    ) -> typing.Optional["abjad_parameters.abc.AbjadAttachment"]:
        """Always return None.

        GraceNoteSequentialEvent can't be initialised from IndicatorCollection.
        """
        return None

    @property
    def is_active(self) -> bool:
        return True

    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        for (
            indicator_to_detach
        ) in (
            abjad_parameters.constants.INDICATORS_TO_DETACH_FROM_MAIN_LEAF_AT_GRACE_NOTES_TUPLE
        ):
            detached_indicator = abjad.detach(indicator_to_detach, leaf)
            abjad.attach(detached_indicator, self._grace_note_sequential_event[0])
        abjad.attach(self._grace_note_sequential_event, leaf)
        return leaf


class AfterGraceNoteSequentialEvent(abjad_parameters.abc.BangLastAttachment):
    def __init__(self, after_grace_note_sequential_event: abjad.AfterGraceContainer):
        self._after_grace_note_sequential_event = after_grace_note_sequential_event

    @classmethod
    def from_indicator_collection(
        cls, indicator_collection: music_parameters.abc.IndicatorCollection
    ) -> typing.Optional["abjad_parameters.abc.AbjadAttachment"]:
        """Always return None.

        AfterGraceNoteSequentialEvent can't be initialised from IndicatorCollection.
        """
        return None

    @property
    def is_active(self) -> bool:
        return True

    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(self._after_grace_note_sequential_event, leaf)
        return leaf


# Auto define all due to many classes
__all__ = tuple(
    name
    for name, cls in globals().items()
    if inspect.isclass(cls)
    and not inspect.isabstract(cls)
    and abjad_parameters.abc.AbjadAttachment in inspect.getmro(cls)
)
