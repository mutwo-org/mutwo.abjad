"""Build Abjad attachments from Mutwo data.
"""

import dataclasses
import inspect
import typing
import warnings

from packaging.version import Version

import abjad  # type: ignore

from mutwo import abjad_parameters
from mutwo import music_parameters
from mutwo import music_version

LeafOrLeafSequence = abjad.Leaf | typing.Sequence[abjad.Leaf]


class Arpeggio(abjad_parameters.abc.BangFirstAttachment):
    _string_to_direction = {
        "up": abjad.enums.UP,
        "down": abjad.enums.DOWN,
        "center": abjad.enums.CENTER,
        "^": abjad.enums.UP,
        "_": abjad.enums.DOWN,
    }

    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        direction = self.indicator.direction
        direction = self._string_to_direction.get(direction, direction)
        abjad.attach(abjad.Arpeggio(direction=direction), leaf)
        return leaf


class Articulation(abjad_parameters.abc.BangEachAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(abjad.Articulation(self.indicator.name), leaf)
        return leaf


class Trill(abjad_parameters.abc.BangFirstAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(abjad.Articulation("trill"), leaf)
        return leaf


class Cue(abjad_parameters.abc.BangFirstAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.Markup(rf"\markup \rounded-box {{ {self.indicator.index} }}"),
            leaf,
            direction=abjad.enums.UP,
        )
        return leaf


class WoodwindFingering(abjad_parameters.abc.BangFirstAttachment):
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
    #'{self.indicator.instrument}
    #'((cc . {self._tuple_to_scheme_list(self.indicator.cc)})
       (lh . {self._tuple_to_scheme_list(self.indicator.left_hand)})
       (rh . {self._tuple_to_scheme_list(self.indicator.right_hand)}))
}}"""

    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        fingering = abjad.LilyPondLiteral(
            f"^\\markup {self._get_markup_content()}", site="after"
        )
        abjad.attach(fingering, leaf)
        return leaf


class Tremolo(abjad_parameters.abc.BangEachAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.StemTremolo(
                self.indicator.flag_count * (2**leaf.written_duration.flag_count)
            ),
            leaf,
        )
        return leaf


class ArtificalHarmonic(abjad_parameters.abc.BangEachAttachment):
    @staticmethod
    def _convert_and_test_leaf(leaf: abjad.Leaf) -> tuple[abjad.Leaf, bool]:
        # return True if artifical_harmonic can be attached and False if
        # artifical harmonic can't be attached

        match leaf:
            case abjad.Chord():
                if len(leaf.note_heads) != 1:
                    warnings.warn(
                        "Can't attach artifical harmonic on chord with more or less"
                        " than one pitch!"
                    )
                    return leaf, False
                return leaf, True
            case abjad.Note():
                new_abjad_leaf = abjad.Chord(
                    [leaf.written_pitch],
                    leaf.written_duration,
                )
                for indicator in abjad.get.indicators(leaf):
                    if type(indicator) != dict:
                        abjad.attach(indicator, new_abjad_leaf)

                return new_abjad_leaf, True
            case _:
                warnings.warn(
                    f"Can't attach artifical harmonic on abjad leaf "
                    f"'{leaf}' of type '{type(leaf)}'!"
                )
                return leaf, False

    def _get_second_pitch(self, abjad_pitch: abjad.Pitch) -> abjad.Pitch:
        return abjad_pitch + self.indicator.semitone_count

    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        leaf, is_attachable = ArtificalHarmonic._convert_and_test_leaf(leaf)
        if is_attachable:
            first_pitch = leaf.note_heads[0].written_pitch
            second_pitch = self._get_second_pitch(first_pitch)
            leaf.written_pitches = abjad.PitchSegment([first_pitch, second_pitch])
            set_note_head_style(leaf, note_head_index=1)
        return leaf


class NaturalHarmonicNodeList(abjad_parameters.abc.AbjadAttachment):
    replace_leaf_by_leaf = False
    # Some indicators are needed for both elements!
    disallow_detach_indicator_list = [abjad.LilyPondLiteral(r"\-", site="after")]

    def process_leaf_tuple(
        self,
        leaf_tuple: tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional[abjad_parameters.abc.AbjadAttachment],
    ) -> typing.Sequence[abjad.Leaf]:
        if len((indicator := self.indicator)) > 2:
            warnings.warn(
                "Can only represent double harmonics, "
                "but not triple or more. The following nodes "
                f"are ignored:\n\n\t{self.indicator[2:]}"
            )
            indicator = indicator[:2]

        stem_direction_tuple = self._node_tuple_to_stem_direction_tuple(
            tuple(indicator)
        )

        # We put each harmonic into its own voice, because we
        # don't want to have all harmonics on the same stem,
        # because then it's not clear for the player which node
        # on which string she or he needs to play. If the stems
        # are separated this is very clear.
        container = abjad.Container([], simultaneous=True)
        for index, data in enumerate(zip(indicator, stem_direction_tuple)):
            node, stem_direction = data
            voice = abjad.Voice([])
            if self.with_duration_line:
                voice.consists_commands.append("Duration_line_engraver")
            for leaf in leaf_tuple:
                leaf = self._leaf_to_chord(leaf)
                if index > 0:  # Avoid indicator duplicates!
                    self._detach_all_indicators(leaf)
                self._process_leaf(leaf, node, stem_direction)
                voice.append(leaf)
            container.append(voice)
        return container

    def _process_leaf(
        self,
        leaf_to_process: abjad.Chord,
        node: music_parameters.NaturalHarmonic.Node,
        stem_direction: bool | type[None],
    ):
        m2a = self.mutwo_pitch_to_abjad_pitch
        pitch_segment = [m2a(node.pitch)]

        if self.indicator.write_string:
            pitch_segment.insert(0, m2a(node.string.tuning_original))

        leaf_to_process.written_pitches = abjad.PitchSegment(pitch_segment)

        if self.indicator.write_string and self.indicator.parenthesize_lower_note_head:
            leaf_to_process.note_heads[0].is_parenthesized = True

        if self.indicator.harmonic_note_head_style:
            set_note_head_style(
                leaf_to_process, note_head_index=int(self.indicator.write_string)
            )

        if stem_direction in (True, False):
            abjad.attach(
                abjad.LilyPondLiteral(
                    r"\once \override Staff.Stem.thickness = 2"
                    "\n"
                    r"\once \override Voice.Stem.direction = "
                    f"{[-1, 1][int(stem_direction)]}",
                    site="before",
                ),
                leaf_to_process,
            )

            if self.with_duration_line:
                abjad.attach(
                    abjad.LilyPondLiteral(
                        r"\once \override Staff.Stem.duration-log = 2"
                        "\n"
                        r"\once \undo \omit Staff.Stem"
                        "\n",
                        site="before",
                    ),
                    leaf_to_process,
                )

        if stem_direction is False:
            abjad.attach(
                abjad.LilyPondLiteral(
                    r"\once \override NoteColumn #'force-hshift = #1.5", site="before"
                ),
                leaf_to_process,
            )

    def _detach_all_indicators(self, leaf_to_process: abjad.Chord):
        for indicator in abjad.get.indicators(leaf_to_process):
            if indicator not in self.disallow_detach_indicator_list:
                abjad.detach(indicator, leaf_to_process)

    @staticmethod
    def _node_tuple_to_stem_direction_tuple(
        node_tuple: tuple[music_parameters.NaturalHarmonic.Node]
        | tuple[
            music_parameters.NaturalHarmonic.Node, music_parameters.NaturalHarmonic.Node
        ]
    ) -> tuple[bool | type[None], ...]:
        if (node_count := len(node_tuple)) == 2:
            node0, node1 = node_tuple  # type: ignore
            if node0.pitch > node1.pitch:
                stem_direction_tuple = (False, True)
            elif node0.pitch == node1.pitch:
                stem_direction_tuple = (True, True)
            else:
                stem_direction_tuple = (True, False)
        elif node_count == 1:
            stem_direction_tuple = (None,)  # type: ignore
        else:
            raise NotImplementedError(node_count)
        return stem_direction_tuple

    @staticmethod
    def _leaf_to_chord(leaf: abjad.Leaf) -> abjad.Chord:
        if isinstance(leaf, abjad.Chord):
            return abjad.mutate.copy(leaf)
        else:
            new_abjad_leaf = abjad.Chord(
                "c",
                leaf.written_duration,
            )
            for indicator in abjad.get.indicators(leaf):
                if type(indicator) != dict:
                    abjad.attach(indicator, new_abjad_leaf)
            return new_abjad_leaf


class StringContactPoint(abjad_parameters.abc.ToggleAttachment):
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
        previous_attachment: typing.Optional[abjad_parameters.abc.AbjadAttachment],
        string_contact_point_markup_string: str,
    ):
        if previous_attachment:
            if previous_attachment.indicator.contact_point == "pizzicato":  # type: ignore
                string_contact_point_markup_string = (
                    rf"\caps {{ \arco {string_contact_point_markup_string} }}"
                )

        final_markup = abjad.LilyPondLiteral(
            rf"^ \markup \fontsize #-2.4 {{ {string_contact_point_markup_string} }}",
            site="absolute_after",
        )
        abjad.attach(
            final_markup,
            leaf,
            direction=abjad.enums.UP,
        )

    def process_leaf(
        self,
        leaf: abjad.Leaf,
        previous_attachment: typing.Optional[abjad_parameters.abc.AbjadAttachment],
    ) -> LeafOrLeafSequence:
        contact_point = self.indicator.contact_point
        if contact_point in self._abbreviation_to_string_contact_point:
            contact_point = self._abbreviation_to_string_contact_point[contact_point]
        try:
            string_contact_point_markup_string = self._string_contact_point_class(
                contact_point
            ).markup_string
        except AssertionError:
            warnings.warn(
                f"Can't find contact point '{self.indicator.contact_point}' "
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
        previous_attachment: typing.Optional[abjad_parameters.abc.AbjadAttachment],
    ) -> tuple[abjad.Leaf, ...]:
        # don't attach ordinario at start (this is the default playing technique)
        if (
            previous_attachment is not None
            or self.indicator.contact_point != "ordinario"
        ):
            return super().process_leaf_tuple(leaf_tuple, previous_attachment)
        else:
            return leaf_tuple


class Pedal(abjad_parameters.abc.ToggleAttachment):
    def process_leaf(
        self,
        leaf: abjad.Leaf,
        previous_attachment: typing.Optional[abjad_parameters.abc.AbjadAttachment],
    ) -> LeafOrLeafSequence:
        if Version(music_version.VERSION) >= Version("0.26.0"):
            pedal_type = self.indicator.type
            pedal_activity = self.indicator.activity
        else:  # BBB
            pedal_type = self.indicator.pedal_type
            pedal_activity = self.indicator.pedal_activity

        if pedal_activity:
            pedal_class = abjad.StartPianoPedal
        else:
            pedal_class = abjad.StopPianoPedal

        abjad.attach(pedal_class(pedal_type), leaf)
        return leaf

    def process_leaf_tuple(
        self,
        leaf_tuple: tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional[abjad_parameters.abc.AbjadAttachment],
    ) -> tuple[abjad.Leaf, ...]:
        # don't attach pedal down at start
        if previous_attachment is not None or self.indicator.is_active:
            return super().process_leaf_tuple(leaf_tuple, previous_attachment)
        else:
            return leaf_tuple


class Slur(abjad_parameters.abc.ToggleAttachment):
    def process_leaf(
        self,
        leaf: abjad.Leaf,
        previous_attachment: typing.Optional[abjad_parameters.abc.AbjadAttachment],
    ) -> LeafOrLeafSequence:
        if self.indicator.activity:
            a = abjad.StartSlur()
        else:
            a = abjad.StopSlur()
        abjad.attach(a, leaf)
        return leaf


class Hairpin(abjad_parameters.abc.ToggleAttachment):
    niente_literal = abjad.LilyPondLiteral(r"\once \override Hairpin.circled-tip = ##t")

    def process_leaf(
        self,
        leaf: abjad.Leaf,
        _: typing.Optional[abjad_parameters.abc.AbjadAttachment],
    ) -> LeafOrLeafSequence:
        if self.indicator.symbol == "!":
            abjad.attach(
                abjad.StopHairpin(),
                leaf,
            )
        else:
            if self.indicator.niente:
                abjad.attach(self.niente_literal, leaf)
            abjad.attach(
                abjad.StartHairpin(self.indicator.symbol),
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
            if self.indicator.niente:
                abjad.attach(self.niente_literal, crescendo_leaf)
            abjad.attach(abjad.StartHairpin("<"), crescendo_leaf)
            decrescendo_leaf = leaf_tuple[int(len(leaf_tuple) // 2)]
            if self.indicator.niente:
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
        if self.indicator.symbol == "<>":
            return self._process_espressivo(leaf_tuple, previous_attachment)
        else:
            return super().process_leaf_tuple(leaf_tuple, previous_attachment)


class BartokPizzicato(
    abjad_parameters.abc.BangFirstAttachment,
):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.LilyPondLiteral("\\snappizzicato", site="after"),
            leaf,
        )
        return leaf


class BreathMark(
    abjad_parameters.abc.BangFirstAttachment,
):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.LilyPondLiteral("\\breathe", site="before"),
            leaf,
        )
        return leaf


class Fermata(abjad_parameters.abc.BangFirstAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.Fermata(self.indicator.type),
            leaf,
        )
        return leaf


class Prall(
    abjad_parameters.abc.BangFirstAttachment,
):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.LilyPondLiteral(r"^\prall", site="after"),
            leaf,
        )
        return leaf


class Tie(
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
    abjad_parameters.abc.BangEachAttachment,
):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        if isinstance(leaf, (abjad.Chord, abjad.Note)):
            abjad.attach(
                abjad.LilyPondLiteral(r"\once \override DurationLine.style = #'trill"),
                leaf,
            )
        return leaf


class DurationLineDashed(
    abjad_parameters.abc.BangEachAttachment,
):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        if isinstance(leaf, (abjad.Chord, abjad.Note)):
            abjad.attach(
                abjad.LilyPondLiteral(
                    r"\once \override DurationLine.style = #'dashed-line"
                ),
                leaf,
            )
        return leaf


class Glissando(
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


class BendAfter(abjad_parameters.abc.BangLastAttachment):
    def _attach_bend_after_to_note(self, note: abjad.Note):
        abjad.attach(
            abjad.LilyPondLiteral(
                "\\once \\override BendAfter.thickness = #'{}".format(
                    self.indicator.thickness
                )
            ),
            note,
        )
        abjad.attach(
            abjad.LilyPondLiteral(
                f"\\once \\override BendAfter.minimum-length = #{self.indicator.minimum_length}"
            ),
            note,
        )
        abjad.attach(
            abjad.LilyPondLiteral("\\once \\override DurationLine.style = #'none"), note
        )
        abjad.attach(abjad.BendAfter(bend_amount=self.indicator.bend_amount), note)

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
    abjad_parameters.abc.BangLastAttachment,
):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.LaissezVibrer(),
            leaf,
        )
        return leaf


class BarLine(abjad_parameters.abc.BangLastAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.BarLine(self.indicator.abbreviation),
            leaf,
        )
        return leaf


class Clef(abjad_parameters.abc.BangFirstAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.Clef(self.indicator.name),
            leaf,
        )
        return leaf


class Ottava(abjad_parameters.abc.ToggleAttachment):
    def process_leaf(
        self,
        leaf: abjad.Leaf,
        previous_attachment: typing.Optional[abjad_parameters.abc.AbjadAttachment],
    ) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.Ottava(self.indicator.octave_count, site="before"),
            leaf,
        )
        return leaf

    def process_leaf_tuple(
        self,
        leaf_tuple: tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional[abjad_parameters.abc.AbjadAttachment],
    ) -> tuple[abjad.Leaf, ...]:
        # don't attach ottava = 0 at start (this is the default notation)
        if previous_attachment is not None or self.indicator.octave_count != 0:
            return super().process_leaf_tuple(leaf_tuple, previous_attachment)
        else:
            return leaf_tuple


class Markup(abjad_parameters.abc.BangFirstAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.Markup(self.indicator.content),
            leaf,
            direction=self.indicator.direction,
        )
        return leaf


class RehearsalMark(abjad_parameters.abc.BangFirstAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(
            abjad.RehearsalMark(markup=self.indicator.markup),
            leaf,
        )
        return leaf


class MarginMarkup(abjad_parameters.abc.BangFirstAttachment):
    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        command = "\\set {}.instrumentName = \\markup ".format(self.indicator.context)
        command += "{ " + self.indicator.content + " }"  # type: ignore
        abjad.attach(
            abjad.LilyPondLiteral(command),
            leaf,
        )
        return leaf


class Ornamentation(abjad_parameters.abc.BangFirstAttachment):
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
            r"\markup { "
            r"\vspace #-0.25 { \fontsize #-4 { "
            rf"\rounded-box {{ {self.indicator.count} "
            r"\hspace #-0.4 \path #0.25 "
            f"{self._direction_to_ornamentation_command[self.indicator.direction]}"
            "}}}}"
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
        cls, indicator_collection: music_parameters.abc.IndicatorCollection, **kwargs
    ) -> typing.Optional[abjad_parameters.abc.AbjadAttachment]:
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
        previous_attachment: typing.Optional[abjad_parameters.abc.AbjadAttachment],
    ) -> LeafOrLeafSequence:
        abjad.attach(abjad.Dynamic(self.dynamic_indicator), leaf)
        return leaf


@dataclasses.dataclass()
class Tempo(abjad_parameters.abc.BangFirstAttachment):
    reference_duration: typing.Optional[tuple[int, int]] = (1, 4)
    units_per_minute: int | tuple[int, int] | None = 60
    textual_indication: typing.Optional[str] = None
    # TODO(for future usage add typing.Literal['rit.', 'acc.'])
    dynamic_change_indication: typing.Optional[str] = None
    stop_dynamic_change_indicaton: bool = False
    print_metronome_mark: bool = True

    @classmethod
    def from_indicator_collection(
        cls, indicator_collection: music_parameters.abc.IndicatorCollection, **kwargs
    ) -> typing.Optional[abjad_parameters.abc.AbjadAttachment]:
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
        cls, indicator_collection: music_parameters.abc.IndicatorCollection, **kwargs
    ) -> typing.Optional[abjad_parameters.abc.AbjadAttachment]:
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


class GraceNoteConsecution(abjad_parameters.abc.BangFirstAttachment):
    def __init__(self, grace_note_consecution: abjad.BeforeGraceContainer):
        self._grace_note_consecution = grace_note_consecution

    @classmethod
    def from_indicator_collection(
        cls, indicator_collection: music_parameters.abc.IndicatorCollection, **kwargs
    ) -> typing.Optional[abjad_parameters.abc.AbjadAttachment]:
        """Always return None.

        GraceNoteConsecution can't be initialised from IndicatorCollection.
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
            abjad.attach(detached_indicator, self._grace_note_consecution[0])
        abjad.attach(self._grace_note_consecution, leaf)
        return leaf


class AfterGraceNoteConsecution(abjad_parameters.abc.BangLastAttachment):
    def __init__(self, after_grace_note_consecution: abjad.AfterGraceContainer):
        self._after_grace_note_consecution = after_grace_note_consecution

    @classmethod
    def from_indicator_collection(
        cls, indicator_collection: music_parameters.abc.IndicatorCollection, **kwargs
    ) -> typing.Optional[abjad_parameters.abc.AbjadAttachment]:
        """Always return None.

        AfterGraceNoteConsecution can't be initialised from IndicatorCollection.
        """
        return None

    @property
    def is_active(self) -> bool:
        return True

    def process_leaf(self, leaf: abjad.Leaf) -> LeafOrLeafSequence:
        abjad.attach(self._after_grace_note_consecution, leaf)
        return leaf


def set_note_head_style(
    leaf: abjad.Chord, note_head_index: int = 0, style: str = "#'harmonic"
):
    abjad.tweak(
        leaf.note_heads[note_head_index],
        abjad.Tweak(rf"\tweak NoteHead.style {style}"),
    )


# Auto define all due to many classes
__all__ = tuple(
    name
    for name, cls in globals().items()
    if inspect.isclass(cls)
    and not inspect.isabstract(cls)
    and abjad_parameters.abc.AbjadAttachment in inspect.getmro(cls)
)
