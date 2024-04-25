"""Module for routines which pre- or postprocess abjad containers."""

import abc
import typing

import abjad

from mutwo import core_events


__all__ = (
    "ProcessAbjadContainerRoutine",
    "AddDurationLineEngraver",
    "PrepareForDurationLineBasedNotation",
    "AddInstrumentName",
    "AddAccidentalStyle",
    "SetStaffSize",
)


class ProcessAbjadContainerRoutine(abc.ABC):
    @abc.abstractmethod
    def __call__(
        self,
        compound_to_convert: core_events.abc.Compound,
        container_to_process: abjad.Container,
    ):
        raise NotImplementedError


class AddDurationLineEngraver(ProcessAbjadContainerRoutine):
    def __call__(
        self,
        compound_to_convert: core_events.abc.Compound,
        container_to_process: abjad.Container,
    ):
        container_to_process.consists_commands.append("Duration_line_engraver")


class PrepareForDurationLineBasedNotation(ProcessAbjadContainerRoutine):
    def __call__(
        self,
        _: core_events.abc.Compound,
        container_to_process: abjad.Container,
    ):
        first_element = abjad.get.leaf(container_to_process, 0)
        before_grace_container = abjad.get.before_grace_container(first_element)
        if before_grace_container:
            first_element = abjad.get.leaf(before_grace_container, 0)
        # don't write rests (simply write empty space)
        abjad.attach(abjad.LilyPondLiteral("\\omit Staff.Rest"), first_element)
        abjad.attach(
            abjad.LilyPondLiteral("\\omit Staff.MultiMeasureRest"), first_element
        )
        # don't write stems (Rhythm get defined by duration line)
        abjad.attach(abjad.LilyPondLiteral("\\omit Staff.Stem"), first_element)
        # don't write flags (Rhythm get defined by duration line)
        abjad.attach(abjad.LilyPondLiteral("\\omit Staff.Flag"), first_element)
        # don't write beams (Rhythm get defined by duration line)
        abjad.attach(abjad.LilyPondLiteral("\\omit Staff.Beam"), first_element)
        # don't write dots (Rhythm get defined by duration line)
        abjad.attach(
            abjad.LilyPondLiteral("\\override Staff.Dots.dot-count = #0"),
            first_element,
        )
        # only write black note heads (Rhythm get defined by duration line)
        abjad.attach(
            abjad.LilyPondLiteral("\\override Staff.NoteHead.duration-log = 2"),
            first_element,
        )


class AddInstrumentName(ProcessAbjadContainerRoutine):
    def __init__(
        self,
        compound_to_instrument_name: typing.Callable[
            [core_events.abc.Compound], str
        ] = lambda compound: compound.instrument_name,
        compound_to_short_instrument_name: typing.Callable[
            [core_events.abc.Compound], str
        ] = lambda compound: compound.short_instrument_name,
        instrument_name_font_size: str = "teeny",
        short_instrument_name_font_size: str = "teeny",
    ):
        self._compound_to_instrument_name = compound_to_instrument_name
        self._compound_to_short_instrument_name = (
            compound_to_short_instrument_name
        )
        self._instrument_name_font_size = instrument_name_font_size
        self._short_instrument_name_font_size = short_instrument_name_font_size

    def __call__(
        self,
        compound_to_convert: core_events.abc.Compound,
        container_to_process: abjad.Container,
    ):
        first_leaf = abjad.get.leaf(container_to_process[0], 0)

        try:
            instrument_name = self._compound_to_instrument_name(
                compound_to_convert
            )
        except AttributeError:
            instrument_name = None

        try:
            short_instrument_name = self._compound_to_short_instrument_name(
                compound_to_convert
            )
        except AttributeError:
            short_instrument_name = None

        lilypond_context = container_to_process.lilypond_context.name

        if instrument_name:
            set_instrument_name_command = (
                f"\\set {lilypond_context}.instrumentName = \\markup {{ "
                f" \\{self._instrument_name_font_size} {{ {instrument_name} }} }}"
            )
            abjad.attach(
                abjad.LilyPondLiteral(set_instrument_name_command),
                first_leaf,
            )
        if short_instrument_name:
            set_short_instrument_name_command = (
                f"\\set {lilypond_context}.shortInstrumentName = \\markup {{ "
                f" \\{self._short_instrument_name_font_size} {{"
                f" {short_instrument_name} }} }}"
            )
            abjad.attach(
                abjad.LilyPondLiteral(set_short_instrument_name_command),
                first_leaf,
            )


class AddAccidentalStyle(ProcessAbjadContainerRoutine):
    def __init__(self, accidental_style: str):
        self._accidental_style = accidental_style

    def __call__(
        self,
        compound_to_convert: core_events.abc.Compound,
        container_to_process: abjad.Container,
    ):
        first_leaf = abjad.get.leaf(container_to_process[0], 0)

        if self._accidental_style:
            abjad.attach(
                abjad.LilyPondLiteral(f'\\accidentalStyle "{self._accidental_style}"'),
                first_leaf,
            )


class SetStaffSize(ProcessAbjadContainerRoutine):
    def __init__(self, difference_of_size: int):
        self._difference_of_size = difference_of_size

    def __call__(
        self,
        compound_to_convert: core_events.abc.Compound,
        container_to_process: abjad.Container,
    ):
        first_leaf = abjad.get.leaf(container_to_process[0], 0)
        abjad.attach(
            abjad.LilyPondLiteral(
                f"\\magnifyStaff #(magstep {self._difference_of_size})",
                format_slot="before",
            ),
            first_leaf,
        )
