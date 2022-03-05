"""Module for routines which pre- or postprocess abjad containers."""

import abc
import typing

import abjad

from mutwo import core_events


__all__ = (
    "ProcessAbjadContainerRoutine",
    "AddDurationLineEngraver",
    "AddInstrumentName",
    "AddAccidentalStyle",
    "SetStaffSize",
)


class ProcessAbjadContainerRoutine(abc.ABC):
    @abc.abstractmethod
    def __call__(
        self,
        complex_event_to_convert: core_events.abc.ComplexEvent,
        container_to_process: abjad.Container,
    ):
        raise NotImplementedError


class AddDurationLineEngraver(ProcessAbjadContainerRoutine):
    def __call__(
        self,
        complex_event_to_convert: core_events.abc.ComplexEvent,
        container_to_process: abjad.Container,
    ):
        container_to_process.consists_commands.append("Duration_line_engraver")


class AddInstrumentName(ProcessAbjadContainerRoutine):
    def __init__(
        self,
        complex_event_to_instrument_name: typing.Callable[
            [core_events.abc.ComplexEvent], str
        ] = lambda complex_event: complex_event.instrument_name,
        complex_event_to_short_instrument_name: typing.Callable[
            [core_events.abc.ComplexEvent], str
        ] = lambda complex_event: complex_event.short_instrument_name,
        instrument_name_font_size: str = "teeny",
        short_instrument_name_font_size: str = "teeny",
    ):
        self._complex_event_to_instrument_name = complex_event_to_instrument_name
        self._complex_event_to_short_instrument_name = (
            complex_event_to_short_instrument_name
        )
        self._instrument_name_font_size = instrument_name_font_size
        self._short_instrument_name_font_size = short_instrument_name_font_size

    def __call__(
        self,
        complex_event_to_convert: core_events.abc.ComplexEvent,
        container_to_process: abjad.Container,
    ):
        first_leaf = abjad.get.leaf(container_to_process[0], 0)

        try:
            instrument_name = self._complex_event_to_instrument_name(
                complex_event_to_convert
            )
        except AttributeError:
            instrument_name = None

        try:
            short_instrument_name = self._complex_event_to_short_instrument_name(
                complex_event_to_convert
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
        complex_event_to_convert: core_events.abc.ComplexEvent,
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
        complex_event_to_convert: core_events.abc.ComplexEvent,
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
