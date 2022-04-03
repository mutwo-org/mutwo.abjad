import abc
import typing

try:
    import quicktions as fractions  # type: ignore
except ImportError:
    import fractions  # type: ignore

import expenvelope  # type: ignore

from mutwo import abjad_parameters
from mutwo import core_converters
from mutwo import core_constants
from mutwo import core_parameters
from mutwo import core_utilities

__all__ = (
    "TempoEnvelopeToAbjadAttachmentTempo",
    "ComplexTempoEnvelopeToAbjadAttachmentTempo",
)


class TempoEnvelopeToAbjadAttachmentTempo(core_converters.abc.Converter):
    """Convert tempo envelope to :class:`~mutwo.converters.frontends.abjad_parameters.Tempo`.

    Abstract base class for tempo envelope conversion. See
    :class:`ComplexTempoEnvelopeToAbjadAttachmentTempo` for a concrete
    class.
    """

    @abc.abstractmethod
    def convert(
        self, tempo_envelope_to_convert: expenvelope.Envelope
    ) -> tuple[tuple[core_constants.Real, abjad_parameters.Tempo], ...]:
        # return tuple filled with subtuples (leaf_index, abjad_parameters.Tempo)
        raise NotImplementedError()


class ComplexTempoEnvelopeToAbjadAttachmentTempo(TempoEnvelopeToAbjadAttachmentTempo):
    """Convert tempo envelope to :class:`~mutwo.converters.frontends.abjad_parameters.Tempo`.

    This object tries to intelligently set correct tempo abjad_parameters to an
    :class:`abjad.Voice` object, appropriate to Western notation standards.
    Therefore it will not repeat tempo indications if they are merely repetitions
    of previous tempo indications and it will write 'a tempo' when returning to the
    same tempo after ritardandi or accelerandi.
    """

    # ###################################################################### #
    #                     private static methods                             #
    # ###################################################################### #

    @staticmethod
    def _convert_tempo_point_tuple(
        tempo_point_tuple: tuple[
            typing.Union[core_constants.Real, core_parameters.TempoPoint], ...
        ]
    ) -> tuple[core_parameters.TempoPoint, ...]:
        return tuple(
            tempo_point
            if isinstance(tempo_point, core_parameters.TempoPoint)
            else core_parameters.TempoPoint(float(tempo_point))
            for tempo_point in tempo_point_tuple
        )

    @staticmethod
    def _find_dynamic_change_indication(
        tempo_point: core_parameters.TempoPoint,
        next_tempo_point: typing.Optional[core_parameters.TempoPoint],
    ) -> typing.Optional[str]:
        dynamic_change_indication = None
        if next_tempo_point:
            absolute_tempo_for_current_tempo_point = (
                tempo_point.absolute_tempo_in_beat_per_minute
            )
            absolute_tempo_for_next_tempo_point = (
                next_tempo_point.absolute_tempo_in_beat_per_minute
            )
            if (
                absolute_tempo_for_current_tempo_point
                > absolute_tempo_for_next_tempo_point
            ):
                dynamic_change_indication = "rit."
            elif (
                absolute_tempo_for_current_tempo_point
                < absolute_tempo_for_next_tempo_point
            ):
                dynamic_change_indication = "acc."

        return dynamic_change_indication

    @staticmethod
    def _shall_write_metronome_mark(
        tempo_envelope_to_convert: expenvelope.Envelope,
        nth_tempo_point: int,
        tempo_point: core_parameters.TempoPoint,
        tempo_points: tuple[core_parameters.TempoPoint, ...],
    ) -> bool:
        write_metronome_mark = True
        for previous_tempo_point, previous_tempo_point_duration in zip(
            reversed(tempo_points[:nth_tempo_point]),
            reversed(tempo_envelope_to_convert.durations[:nth_tempo_point]),
        ):
            # make sure the previous tempo point could have been written
            # down (longer duration than minimal duration)
            if previous_tempo_point_duration > 0:
                # if the previous writeable MetronomeMark has the same
                # beats per minute than the current event, there is no
                # need to write it down again
                if (
                    previous_tempo_point.absolute_tempo_in_beat_per_minute
                    == tempo_point.absolute_tempo_in_beat_per_minute
                ):
                    write_metronome_mark = False
                    break

                # but if it differs, we should definitely write it down
                else:
                    break

        return write_metronome_mark

    @staticmethod
    def _shall_stop_dynamic_change_indication(
        tempo_attachment_tuple: tuple[
            tuple[core_constants.Real, abjad_parameters.Tempo], ...
        ]
    ) -> bool:
        stop_dynamic_change_indicaton = False
        for _, previous_tempo_attachment in reversed(tempo_attachment_tuple):
            # make sure the previous tempo point could have been written
            # down (longer duration than minimal duration)
            if previous_tempo_attachment.dynamic_change_indication is not None:
                stop_dynamic_change_indicaton = True
            break

        return stop_dynamic_change_indicaton

    @staticmethod
    def _find_metronome_mark_values(
        write_metronome_mark: bool,
        tempo_point: core_parameters.TempoPoint,
        stop_dynamic_change_indicaton: bool,
    ) -> tuple[
        typing.Optional[tuple[int, int]],
        typing.Optional[typing.Union[int, tuple[int, int]]],
        typing.Optional[str],
    ]:
        if write_metronome_mark:
            textual_indication: typing.Optional[str] = tempo_point.textual_indication
            reference = fractions.Fraction(tempo_point.reference) * fractions.Fraction(
                1, 4
            )
            reference_duration: typing.Optional[tuple[int, int]] = (
                reference.numerator,
                reference.denominator,
            )
            units_per_minute: typing.Optional[typing.Union[int, tuple[int, int]]] = (
                (
                    int(tempo_point.tempo_or_tempo_range_in_beats_per_minute[0]),
                    int(tempo_point.tempo_or_tempo_range_in_beats_per_minute[1]),
                )
                if isinstance(
                    tempo_point.tempo_or_tempo_range_in_beats_per_minute, tuple
                )
                else int(tempo_point.tempo_or_tempo_range_in_beats_per_minute)
            )

        else:
            reference_duration = None
            units_per_minute = None
            # check if you can write 'a tempo'
            if stop_dynamic_change_indicaton:
                textual_indication = "a tempo"
            else:
                textual_indication = None

        return reference_duration, units_per_minute, textual_indication

    @staticmethod
    def _process_tempo_event(
        tempo_envelope_to_convert: expenvelope.Envelope,
        nth_tempo_point: int,
        tempo_point: core_parameters.TempoPoint,
        tempo_point_tuple: tuple[core_parameters.TempoPoint, ...],
        tempo_attachment_tuple: tuple[
            tuple[core_constants.Real, abjad_parameters.Tempo], ...
        ],
    ) -> abjad_parameters.Tempo:
        try:
            next_tempo_point: typing.Optional[
                core_parameters.TempoPoint
            ] = tempo_point_tuple[nth_tempo_point + 1]
        except IndexError:
            next_tempo_point = None

        # check for dynamic_change_indication
        dynamic_change_indication = (
            ComplexTempoEnvelopeToAbjadAttachmentTempo._find_dynamic_change_indication(
                tempo_point, next_tempo_point
            )
        )
        write_metronome_mark = (
            ComplexTempoEnvelopeToAbjadAttachmentTempo._shall_write_metronome_mark(
                tempo_envelope_to_convert,
                nth_tempo_point,
                tempo_point,
                tempo_point_tuple,
            )
        )

        stop_dynamic_change_indicaton = ComplexTempoEnvelopeToAbjadAttachmentTempo._shall_stop_dynamic_change_indication(
            tempo_attachment_tuple
        )

        (
            reference_duration,
            units_per_minute,
            textual_indication,
        ) = ComplexTempoEnvelopeToAbjadAttachmentTempo._find_metronome_mark_values(
            write_metronome_mark, tempo_point, stop_dynamic_change_indicaton
        )

        # for writing 'a tempo'
        if textual_indication == "a tempo":
            write_metronome_mark = True

        converted_tempo_point = abjad_parameters.Tempo(
            reference_duration=reference_duration,
            units_per_minute=units_per_minute,
            textual_indication=textual_indication,
            dynamic_change_indication=dynamic_change_indication,
            stop_dynamic_change_indicaton=stop_dynamic_change_indicaton,
            print_metronome_mark=write_metronome_mark,
        )

        return converted_tempo_point

    # ###################################################################### #
    #                           public api                                   #
    # ###################################################################### #

    def convert(
        self, tempo_envelope_to_convert: expenvelope.Envelope
    ) -> tuple[tuple[core_constants.Real, abjad_parameters.Tempo], ...]:
        tempo_point_tuple = (
            ComplexTempoEnvelopeToAbjadAttachmentTempo._convert_tempo_point_tuple(
                tempo_envelope_to_convert.levels
            )
        )

        tempo_attachment_list: list[
            tuple[core_constants.Real, abjad_parameters.Tempo]
        ] = []
        for nth_tempo_point, absolute_time, duration, tempo_point in zip(
            range(len(tempo_point_tuple)),
            core_utilities.accumulate_from_zero(tempo_envelope_to_convert.durations),
            tempo_envelope_to_convert.durations + (1,),
            tempo_point_tuple,
        ):

            if duration > 0:
                tempo_attachment = (
                    ComplexTempoEnvelopeToAbjadAttachmentTempo._process_tempo_event(
                        tempo_envelope_to_convert,
                        nth_tempo_point,
                        tempo_point,
                        tempo_point_tuple,
                        tuple(tempo_attachment_list),
                    )
                )
                tempo_attachment_list.append((absolute_time, tempo_attachment))

        return tuple(tempo_attachment_list)
