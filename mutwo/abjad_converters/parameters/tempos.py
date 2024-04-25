import abc
import typing

try:
    import quicktions as fractions  # type: ignore
except ImportError:
    import fractions  # type: ignore

from mutwo import abjad_parameters
from mutwo import core_converters
from mutwo import core_constants
from mutwo import core_parameters
from mutwo import core_utilities

__all__ = (
    "TempoToAbjadAttachmentTempo",
    "ComplexTempoToAbjadAttachmentTempo",
)


class TempoToAbjadAttachmentTempo(core_converters.abc.Converter):
    """Convert tempo envelope to :class:`~mutwo.abjad_parameters.Tempo`.

    Abstract base class for tempo envelope conversion. See
    :class:`ComplexTempoToAbjadAttachmentTempo` for a concrete
    class.
    """

    @abc.abstractmethod
    def convert(
        self, tempo_to_convert: core_parameters.abc.Tempo
    ) -> tuple[tuple[core_constants.Real, abjad_parameters.Tempo], ...]:
        # return tuple filled with subtuples (leaf_index, abjad_parameters.Tempo)
        raise NotImplementedError()


class ComplexTempoToAbjadAttachmentTempo(TempoToAbjadAttachmentTempo):
    """Convert tempo to :class:`~mutwo.abjad_parameters.Tempo`.

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
    def _convert_tempo_tuple(
        tempo_tuple: tuple[
            typing.Union[core_constants.Real, core_parameters.abc.Tempo], ...
        ]
    ) -> tuple[core_parameters.abc.Tempo, ...]:
        return tuple(
            tempo
            if isinstance(tempo, core_parameters.abc.Tempo)
            else core_parameters.DirectTempo(float(tempo))
            for tempo in tempo_tuple
        )

    @staticmethod
    def _find_dynamic_change_indication(
        tempo: core_parameters.abc.Tempo,
        next_tempo: typing.Optional[core_parameters.abc.Tempo],
    ) -> typing.Optional[str]:
        dynamic_change_indication = None
        if next_tempo:
            absolute_tempo_for_current_tempo = tempo.bpm
            absolute_tempo_for_next_tempo = next_tempo.bpm
            if absolute_tempo_for_current_tempo > absolute_tempo_for_next_tempo:
                dynamic_change_indication = "rit."
            elif absolute_tempo_for_current_tempo < absolute_tempo_for_next_tempo:
                dynamic_change_indication = "acc."

        return dynamic_change_indication

    @staticmethod
    def _shall_write_metronome_mark(
        tempo_to_convert: core_parameters.FlexTempo,
        tempo_index: int,
        tempo: core_parameters.abc.Tempo,
        tempo_tuple: tuple[core_parameters.abc.Tempo, ...],
    ) -> bool:
        write_metronome_mark = True
        for previous_tempo, previous_tempo_duration in zip(
            reversed(tempo_tuple[:tempo_index]),
            reversed(tempo_to_convert.get_parameter("duration")[:tempo_index]),
        ):
            # make sure the previous tempo point could have been written
            # down (longer duration than minimal duration)
            if previous_tempo_duration > 0:
                # if the previous writeable MetronomeMark has the same
                # beats per minute than the current event, there is no
                # need to write it down again
                if previous_tempo.bpm == tempo.bpm:
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
        tempo: core_parameters.abc.Tempo,
        stop_dynamic_change_indicaton: bool,
    ) -> tuple[
        typing.Optional[tuple[int, int]],
        typing.Optional[typing.Union[int, tuple[int, int]]],
        typing.Optional[str],
    ]:
        if write_metronome_mark:
            textual_indication: typing.Optional[str] = getattr(
                tempo, "textual_indication", None
            )
            reference = fractions.Fraction(getattr(tempo, "reference", 1))
            reference_duration: typing.Optional[tuple[int, int]] = (
                reference.numerator,
                reference.denominator,
            )

            if hasattr(tempo, "bpm_range"):
                if (b := tempo.bpm_range.start) != tempo.bpm_range.end:
                    units_per_minute = (
                        int(tempo.bpm_range.start),
                        int(tempo.bpm_range.end),
                    )
                else:
                    units_per_minute = int(b)
            else:
                units_per_minute = int(tempo.bpm)

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
    def _process_tempo_chronon(
        tempo_to_convert: core_parameters.FlexTempo,
        tempo_index: int,
        tempo: core_parameters.abc.Tempo,
        tempo_tuple: tuple[core_parameters.abc.Tempo, ...],
        tempo_attachment_tuple: tuple[
            tuple[core_constants.Real, abjad_parameters.Tempo], ...
        ],
    ) -> abjad_parameters.Tempo:
        try:
            next_tempo: typing.Optional[core_parameters.abc.Tempo] = tempo_tuple[
                tempo_index + 1
            ]
        except IndexError:
            next_tempo = None

        # check for dynamic_change_indication
        dynamic_change_indication = (
            ComplexTempoToAbjadAttachmentTempo._find_dynamic_change_indication(
                tempo, next_tempo
            )
        )

        write_metronome_mark = (
            ComplexTempoToAbjadAttachmentTempo._shall_write_metronome_mark(
                tempo_to_convert,
                tempo_index,
                tempo,
                tempo_tuple,
            )
        )

        stop_dynamic_change_indicaton = (
            ComplexTempoToAbjadAttachmentTempo._shall_stop_dynamic_change_indication(
                tempo_attachment_tuple
            )
        )

        (
            reference_duration,
            units_per_minute,
            textual_indication,
        ) = ComplexTempoToAbjadAttachmentTempo._find_metronome_mark_values(
            write_metronome_mark, tempo, stop_dynamic_change_indicaton
        )

        # for writing 'a tempo'
        if textual_indication == "a tempo":
            write_metronome_mark = True

        converted_tempo = abjad_parameters.Tempo(
            reference_duration=reference_duration,
            units_per_minute=units_per_minute,
            textual_indication=textual_indication,
            dynamic_change_indication=dynamic_change_indication,
            stop_dynamic_change_indicaton=stop_dynamic_change_indicaton,
            print_metronome_mark=write_metronome_mark,
        )

        return converted_tempo

    # ###################################################################### #
    #                           public api                                   #
    # ###################################################################### #

    def convert(
        self, tempo_to_convert: core_parameters.abc.Tempo
    ) -> tuple[tuple[core_constants.Real, abjad_parameters.Tempo], ...]:
        if isinstance(tempo_to_convert, core_parameters.FlexTempo):
            flex_tempo_to_convert = tempo_to_convert
        else:
            flex_tempo_to_convert = core_parameters.FlexTempo([[0, tempo_to_convert]])

        tempo_tuple = ComplexTempoToAbjadAttachmentTempo._convert_tempo_tuple(
            tuple(flex_tempo_to_convert.parameter_tuple)
        )
        print(tempo_tuple)

        tempo_attachment_list: list[
            tuple[core_constants.Real, abjad_parameters.Tempo]
        ] = []
        for tempo_index, absolute_time, duration, tempo in zip(
            range(len(tempo_tuple)),
            core_utilities.accumulate_from_n(
                flex_tempo_to_convert.get_parameter("duration"),
                core_parameters.DirectDuration(0),
            ),
            tuple(flex_tempo_to_convert.get_parameter("duration")) + (1,),
            tempo_tuple,
        ):
            tempo_attachment = (
                ComplexTempoToAbjadAttachmentTempo._process_tempo_chronon(
                    flex_tempo_to_convert,
                    tempo_index,
                    tempo,
                    tempo_tuple,
                    tuple(tempo_attachment_list),
                )
            )
            tempo_attachment_list.append((absolute_time, tempo_attachment))

        return tuple(tempo_attachment_list)
