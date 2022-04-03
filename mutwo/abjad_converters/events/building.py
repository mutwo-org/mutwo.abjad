"""Module to build complex multi-level abjad based scores from mutwo events."""

import abc
import inspect
import itertools
import typing

try:
    import quicktions as fractions  # type: ignore
except ImportError:
    import fractions  # type: ignore

import abjad  # type: ignore

from mutwo import abjad_converters
from mutwo import abjad_parameters
from mutwo import core_converters
from mutwo import core_events
from mutwo import core_utilities
from mutwo import music_converters
from mutwo import music_parameters

from ..parameters import MutwoPitchToAbjadPitch
from ..parameters import MutwoVolumeToAbjadAttachmentDynamic
from ..parameters import TempoEnvelopeToAbjadAttachmentTempo
from ..parameters import ComplexTempoEnvelopeToAbjadAttachmentTempo
from ..parameters import MutwoLyricToAbjadString

from .quantization import SequentialEventToQuantizedAbjadContainer
from .quantization import NauertSequentialEventToQuantizedAbjadContainer

# from .quantization import RMakersSequentialEventToQuantizedAbjadContainer
from .quantization import (
    NauertSequentialEventToDurationLineBasedQuantizedAbjadContainerConverter,
)
from .quantization import (
    RMakersSequentialEventToDurationLineBasedQuantizedAbjadContainerConverter,
)


__all__ = (
    "ComplexEventToAbjadContainer",
    "SequentialEventToAbjadVoice",
    "NestedComplexEventToAbjadContainer",
    "NestedComplexEventToComplexEventToAbjadContainers",
    "CycleBasedNestedComplexEventToComplexEventToAbjadContainers",
    "TagBasedNestedComplexEventToComplexEventToAbjadContainers",
)


class ComplexEventToAbjadContainer(core_converters.abc.Converter):
    def __init__(
        self,
        abjad_container_class: typing.Type[abjad.Container],
        lilypond_type_of_abjad_container: str,
        complex_event_to_abjad_container_name: typing.Callable[
            [core_events.abc.ComplexEvent], str
        ],
        pre_process_abjad_container_routine_sequence: typing.Sequence[
            abjad_converters.ProcessAbjadContainerRoutine
        ],
        post_process_abjad_container_routine_sequence: typing.Sequence[
            abjad_converters.ProcessAbjadContainerRoutine
        ],
    ):
        self._abjad_container_class = abjad_container_class
        self._lilypond_type_of_abjad_container = lilypond_type_of_abjad_container
        self._complex_event_to_abjad_container_name = (
            complex_event_to_abjad_container_name
        )
        self._pre_process_abjad_container_routine_sequence = (
            pre_process_abjad_container_routine_sequence
        )
        self._post_process_abjad_container_routine_sequence = (
            post_process_abjad_container_routine_sequence
        )

    def _make_empty_abjad_container(
        self, complex_event_to_converter: core_events.abc.ComplexEvent
    ) -> abjad.Container:
        abjad_container_name = core_utilities.call_function_except_attribute_error(
            self._complex_event_to_abjad_container_name,
            complex_event_to_converter,
            None,
        )

        kwargs = {}

        argument_tuple = tuple(
            inspect.signature(self._abjad_container_class).parameters.keys()
        )

        if "simultaneous" in argument_tuple:
            kwargs.update(
                {
                    "simultaneous": isinstance(
                        complex_event_to_converter, core_events.SimultaneousEvent
                    )
                }
            )

        if abjad_container_name and "name" in argument_tuple:
            kwargs.update({"name": abjad_container_name})

        if self._lilypond_type_of_abjad_container and "lilypond_type" in argument_tuple:
            kwargs.update({"lilypond_type": self._lilypond_type_of_abjad_container})

        return self._abjad_container_class([], **kwargs)

    def _pre_process_abjad_container(
        self,
        complex_event_to_convert: core_events.abc.ComplexEvent,
        abjad_container_to_pre_process: abjad.Container,
    ):
        for (
            pre_process_abjad_container_routine
        ) in self._pre_process_abjad_container_routine_sequence:
            pre_process_abjad_container_routine(
                complex_event_to_convert, abjad_container_to_pre_process
            )

    def _post_process_abjad_container(
        self,
        complex_event_to_convert: core_events.abc.ComplexEvent,
        abjad_container_to_post_process: abjad.Container,
    ):
        for (
            post_process_abjad_container_routine
        ) in self._post_process_abjad_container_routine_sequence:
            post_process_abjad_container_routine(
                complex_event_to_convert, abjad_container_to_post_process
            )

    @abc.abstractmethod
    def _fill_abjad_container(
        self,
        abjad_container_to_fill: abjad.Container,
        complex_event_to_convert: core_events.abc.ComplexEvent,
    ):
        raise NotImplementedError

    def convert(
        self, complex_event_to_convert: core_events.abc.ComplexEvent
    ) -> abjad.Container:
        abjad_container = self._make_empty_abjad_container(complex_event_to_convert)
        self._pre_process_abjad_container(complex_event_to_convert, abjad_container)
        self._fill_abjad_container(abjad_container, complex_event_to_convert)
        self._post_process_abjad_container(complex_event_to_convert, abjad_container)
        return abjad_container


class SequentialEventToAbjadVoice(ComplexEventToAbjadContainer):
    """Convert :class:`~mutwo.core_events.SequentialEvent` to :class:`abjad.Voice`.

    :param sequential_event_to_quantized_abjad_container_converter: Class which
        defines how the Mutwo data will be quantized. See
        :class:`SequentialEventToQuantizedAbjadContainer` for more information.
    :type sequential_event_to_quantized_abjad_container_converter: SequentialEventToQuantizedAbjadContainer, optional
    :param simple_event_to_pitch_list: Function to extract from a
        :class:`mutwo.core_events.SimpleEvent` a tuple that contains pitch objects
        (objects that inherit from :class:`mutwo.music_parameters.abc.Pitch`).
        By default it asks the Event for its
        :attr:`~mutwo.events.music.NoteLike.pitch_list` attribute
        (because by default :class:`mutwo.events.music.NoteLike` objects are expected).
        When using different Event classes than :class:`~mutwo.events.music.NoteLike`
        with a different name for their pitch property, this argument
        should be overridden.
        If the function call raises an :obj:`AttributeError` (e.g. if no pitch can be
        extracted), mutwo will assume an event without any pitches.
    :type simple_event_to_pitch_list: typing.Callable[[core_events.SimpleEvent], music_parameters.abc.Pitch], optional
    :param simple_event_to_volume: Function to extract the volume from a
        :class:`mutwo.core_events.SimpleEvent` in the purpose of generating dynamic
        indicators. The function should return an object that inherits from
        :class:`mutwo.music_parameters.abc.Volume`. By default it asks the Event for
        its :attr:`~mutwo.events.music.NoteLike.volume` attribute (because by default
        :class:`mutwo.events.music.NoteLike` objects are expected).
        When using different Event classes than :class:`~mutwo.events.music.NoteLike`
        with a different name for their volume property, this argument should
        be overridden.
        If the function call raises an :obj:`AttributeError` (e.g. if no volume can be
        extracted), mutwo will set :attr:`pitch_list` to an empty list and set
        volume to 0.
    :type simple_event_to_volume: typing.Callable[[core_events.SimpleEvent], music_parameters.abc.Volume], optional
    :param simple_event_to_grace_note_sequential_event: Function to extract from a
        :class:`mutwo.core_events.SimpleEvent` a
        :class:`~mutwo.core_events.SequentialEvent`
        object filled with
        :class:`~mutwo.core_events.SimpleEvent`.
        By default it asks the Event for its
        :attr:`~mutwo.events.music.NoteLike.grace_note_sequential_event`
        attribute (because by default :class:`mutwo.events.music.NoteLike`
        objects are expected).
        When using different Event classes than :class:`~mutwo.events.music.NoteLike`
        with a different name for their `grace_note_sequential_event` property, this argument
        should be overridden. If the
        function call raises an :obj:`AttributeError` (e.g. if no grace_note_sequential_event can be
        extracted), mutwo will use an empty
        :class:`~mutwo.core_events.SequentialEvent`.
    :type simple_event_to_grace_note_sequential_event: typing.Callable[[core_events.SimpleEvent], core_events.SequentialEvent[core_events.SimpleEvent]], optional
    :param simple_event_to_after_grace_note_sequential_event: Function to extract from a
        :class:`mutwo.core_events.SimpleEvent` a
        :class:`~mutwo.core_events.SequentialEvent`
        object filled with
        :class:`~mutwo.core_events.SimpleEvent`.
        By default it asks the Event for its
        :attr:`~mutwo.events.music.NoteLike.after_grace_note_sequential_event`
        attribute (because by default :class:`mutwo.events.music.NoteLike`
        objects are expected).
        When using different Event classes than :class:`~mutwo.events.music.NoteLike`
        with a different name for their `after_grace_note_sequential_event` property, this
        argument should be overridden. If the function call
        raises an :obj:`AttributeError` (e.g. if no after_grace_note_sequential_event can be
        extracted), mutwo will use an empty
        :class:`~mutwo.core_events.SequentialEvent`.
    :type simple_event_to_after_grace_note_sequential_event: typing.Callable[[core_events.SimpleEvent], core_events.SequentialEvent[core_events.SimpleEvent]], optional
    :param simple_event_to_playing_indicator_collection: Function to extract from a
        :class:`mutwo.core_events.SimpleEvent` a
        :class:`mutwo.music_parameters.playing_indicators.PlayingIndicatorCollection`
        object. By default it asks the Event for its
        :attr:`~mutwo.events.music.NoteLike.playing_indicator_collection`
        attribute (because by default :class:`mutwo.events.music.NoteLike`
        objects are expected).
        When using different Event classes than :class:`~mutwo.events.music.NoteLike`
        with a different name for their playing_indicators property, this argument
        should be overridden. If the
        function call raises an :obj:`AttributeError` (e.g. if no playing indicator
        collection can be extracted), mutwo will build a playing indicator collection
        from :const:`~mutwo.music_events.configurations.DEFAULT_PLAYING_INDICATORS_COLLECTION_CLASS`.
    :type simple_event_to_playing_indicator_collection: typing.Callable[[core_events.SimpleEvent], music_parameters.PlayingIndicatorCollection,], optional
    :param simple_event_to_notation_indicator_collection: Function to extract from a
        :class:`mutwo.core_events.SimpleEvent` a
        :class:`mutwo.music_parameters.notation_indicators.NotationIndicatorCollection`
        object. By default it asks the Event for its
        :attr:`~mutwo.events.music.NoteLike.notation_indicators`
        (because by default :class:`mutwo.events.music.NoteLike` objects are expected).
        When using different Event classes than ``NoteLike`` with a different name for
        their playing_indicators property, this argument should be overridden. If the
        function call raises an :obj:`AttributeError` (e.g. if no notation indicator
        collection can be extracted), mutwo will build a notation indicator collection
        from :const:`~mutwo.music_events.configurations.DEFAULT_NOTATION_INDICATORS_COLLECTION_CLASS`
    :type simple_event_to_notation_indicator_collection: typing.Callable[[core_events.SimpleEvent], music_parameters.NotationIndicatorCollection,], optional
    :param simple_event_to_lyric: Function to extract the lyric from a
        :class:`mutwo.core_events.SimpleEvent` in the purpose of generating lyrics.
        The function should return an object that inherits from
        :class:`mutwo.music_parameters.abc.Lyric`. By default it asks the Event for
        its :attr:`~mutwo.events.music.NoteLike.lyric` attribute (because by default
        :class:`mutwo.events.music.NoteLike` objects are expected).
        When using different Event classes than :class:`~mutwo.events.music.NoteLike`
        with a different name for their lyric property, this argument should
        be overridden.
        If the function call raises an :obj:`AttributeError` (e.g. if no lyric can be
        extracted), mutwo will set :attr:`lyric` to an empty text.
    :type simple_event_to_lyric: typing.Callable[[core_events.SimpleEvent], music_parameters.abc.Lyric], optional
    :param is_simple_event_rest: Function to detect if the
        the inspected :class:`mutwo.core_events.SimpleEvent` is a Rest. By
        default Mutwo simply checks if 'pitch_list' contain any objects. If not,
        the Event will be interpreted as a rest.
    :type is_simple_event_rest: typing.Callable[[core_events.SimpleEvent], bool], optional
    :param mutwo_pitch_to_abjad_pitch_converter: Class which defines how to convert
        :class:`mutwo.music_parameters.abc.Pitch` objects to :class:`abjad.Pitch` objects.
        See :class:`MutwoPitchToAbjadPitch` for more information.
    :type mutwo_pitch_to_abjad_pitch_converter: MutwoPitchToAbjadPitch, optional
    :param mutwo_volume_to_abjad_attachment_dynamic_converter: Class which defines how
        to convert :class:`mutwo.music_parameters.abc.Volume` objects to
        :class:`mutwo.converters.frontends.abjad_parameters.Dynamic` objects.
        See :class:`MutwoVolumeToAbjadAttachmentDynamic` for more information.
    :type mutwo_volume_to_abjad_attachment_dynamic_converter: MutwoVolumeToAbjadAttachmentDynamic, optional
    :param tempo_envelope_to_abjad_attachment_tempo_converter: Class which defines how
        to convert tempo envelopes to
        :class:`mutwo.converters.frontends.abjad_parameters.Tempo` objects.
        See :class:`TempoEnvelopeToAbjadAttachmentTempo` for more information.
    :type tempo_envelope_to_abjad_attachment_tempo_converter: TempoEnvelopeToAbjadAttachmentTempo, optional
    :param mutwo_lyric_to_abjad_string: Callable which defines how
        to convert :class:`mutwo.music_parameters.abc.Lyric` to a string.
        Consult :class:`mutwo.abjad_converters.MutwoLyricToAbjadString`
        for more information.
    :type mutwo_lyric_to_abjad_string: MutwoLyricToAbjadString
    :param abjad_attachment_class_sequence: A tuple which contains all available abjad attachment classes
        which shall be used by the converter.
    :type abjad_attachment_class_sequence: typing.Sequence[abjad_parameters.abc.AbjadAttachment], optional
    :param write_multimeasure_rests: Set to ``True`` if the converter should replace
        rests that last a complete bar with multimeasure rests (rests with uppercase
        "R" in Lilypond). Default to ``True``.
    :type write_multimeasure_rests: bool
    """

    ExtractedData = tuple[
        list[music_parameters.abc.Pitch],
        music_parameters.abc.Volume,
        core_events.SequentialEvent[core_events.SimpleEvent],
        core_events.SequentialEvent[core_events.SimpleEvent],
        music_parameters.PlayingIndicatorCollection,
        music_parameters.NotationIndicatorCollection,
        music_parameters.abc.Lyric,
    ]

    ExtractedDataPerSimpleEvent = tuple[ExtractedData, ...]

    def __init__(
        self,
        sequential_event_to_quantized_abjad_container_converter: SequentialEventToQuantizedAbjadContainer = NauertSequentialEventToQuantizedAbjadContainer(),
        simple_event_to_pitch_list: typing.Callable[
            [core_events.SimpleEvent], list[music_parameters.abc.Pitch]
        ] = music_converters.SimpleEventToPitchList(),
        simple_event_to_volume: typing.Callable[
            [core_events.SimpleEvent], music_parameters.abc.Volume
        ] = music_converters.SimpleEventToVolume(),
        simple_event_to_grace_note_sequential_event: typing.Callable[
            [core_events.SimpleEvent],
            core_events.SequentialEvent[core_events.SimpleEvent],
        ] = music_converters.SimpleEventToGraceNoteSequentialEvent(),
        simple_event_to_after_grace_note_sequential_event: typing.Callable[
            [core_events.SimpleEvent],
            core_events.SequentialEvent[core_events.SimpleEvent],
        ] = music_converters.SimpleEventToAfterGraceNoteSequentialEvent(),
        simple_event_to_playing_indicator_collection: typing.Callable[
            [core_events.SimpleEvent],
            music_parameters.PlayingIndicatorCollection,
        ] = music_converters.SimpleEventToPlayingIndicatorCollection(),
        simple_event_to_notation_indicator_collection: typing.Callable[
            [core_events.SimpleEvent],
            music_parameters.NotationIndicatorCollection,
        ] = music_converters.SimpleEventToNotationIndicatorCollection(),
        simple_event_to_lyric: typing.Callable[
            [core_events.SimpleEvent],
            music_parameters.abc.Lyric,
        ] = music_converters.SimpleEventToLyric(),
        is_simple_event_rest: typing.Callable[[core_events.SimpleEvent], bool] = None,
        mutwo_pitch_to_abjad_pitch_converter: MutwoPitchToAbjadPitch = MutwoPitchToAbjadPitch(),
        mutwo_volume_to_abjad_attachment_dynamic_converter: typing.Optional[
            MutwoVolumeToAbjadAttachmentDynamic
        ] = MutwoVolumeToAbjadAttachmentDynamic(),
        tempo_envelope_to_abjad_attachment_tempo_converter: typing.Optional[
            TempoEnvelopeToAbjadAttachmentTempo
        ] = ComplexTempoEnvelopeToAbjadAttachmentTempo(),
        mutwo_lyric_to_abjad_string: MutwoLyricToAbjadString = MutwoLyricToAbjadString(),
        abjad_attachment_class_sequence: typing.Sequence[
            typing.Type[abjad_parameters.abc.AbjadAttachment]
        ] = None,
        write_multimeasure_rests: bool = True,
        abjad_container_class: typing.Type[abjad.Container] = abjad.Voice,
        lilypond_type_of_abjad_container: str = "Voice",
        complex_event_to_abjad_container_name: typing.Callable[
            [core_events.abc.ComplexEvent], typing.Optional[str]
        ] = lambda _: None,
        pre_process_abjad_container_routine_sequence: typing.Sequence[
            abjad_converters.ProcessAbjadContainerRoutine
        ] = tuple([]),
        post_process_abjad_container_routine_sequence: typing.Sequence[
            abjad_converters.ProcessAbjadContainerRoutine
        ] = tuple([]),
    ):
        # special treatment for duration line based quantizer
        if isinstance(
            sequential_event_to_quantized_abjad_container_converter,
            (
                NauertSequentialEventToDurationLineBasedQuantizedAbjadContainerConverter,
                RMakersSequentialEventToDurationLineBasedQuantizedAbjadContainerConverter,
            ),
        ):
            post_process_abjad_container_routine_sequence += (
                abjad_converters.AddDurationLineEngraver(),
            )

        super().__init__(
            abjad_container_class,
            lilypond_type_of_abjad_container,
            complex_event_to_abjad_container_name,
            pre_process_abjad_container_routine_sequence,
            post_process_abjad_container_routine_sequence,
        )

        if abjad_attachment_class_sequence is None:
            abjad_attachment_class_sequence = (
                abjad_converters.configurations.DEFAULT_ABJAD_ATTACHMENT_CLASS_TUPLE
            )
        else:
            abjad_attachment_class_sequence = tuple(abjad_attachment_class_sequence)

        if is_simple_event_rest is None:

            def is_simple_event_rest(simple_event: core_events.SimpleEvent) -> bool:
                pitch_list = core_utilities.call_function_except_attribute_error(
                    simple_event_to_pitch_list, simple_event, []
                )
                return not bool(pitch_list)

        self._abjad_attachment_class_sequence = abjad_attachment_class_sequence

        self._available_attachment_tuple = tuple(
            abjad_attachment_class.get_class_name()
            for abjad_attachment_class in self._abjad_attachment_class_sequence
        )

        self._sequential_event_to_quantized_abjad_container_converter = (
            sequential_event_to_quantized_abjad_container_converter
        )

        self._simple_event_to_pitch_list = simple_event_to_pitch_list
        self._simple_event_to_volume = simple_event_to_volume
        self._simple_event_to_grace_note_sequential_event = (
            simple_event_to_grace_note_sequential_event
        )
        self._simple_event_to_after_grace_note_sequential_event = (
            simple_event_to_after_grace_note_sequential_event
        )
        self._simple_event_to_playing_indicator_collection = (
            simple_event_to_playing_indicator_collection
        )
        self._simple_event_to_notation_indicator_collection = (
            simple_event_to_notation_indicator_collection
        )
        self._simple_event_to_lyric = simple_event_to_lyric
        self._simple_event_to_function_tuple = (
            self._simple_event_to_grace_note_sequential_event,
            self._simple_event_to_after_grace_note_sequential_event,
            self._simple_event_to_playing_indicator_collection,
            self._simple_event_to_notation_indicator_collection,
            self._simple_event_to_lyric,
        )

        self._is_simple_event_rest = is_simple_event_rest
        self._mutwo_pitch_to_abjad_pitch_converter = (
            mutwo_pitch_to_abjad_pitch_converter
        )

        self._mutwo_volume_to_abjad_attachment_dynamic_converter = (
            mutwo_volume_to_abjad_attachment_dynamic_converter
        )
        if tempo_envelope_to_abjad_attachment_tempo_converter:
            tempo_attachment_tuple = tempo_envelope_to_abjad_attachment_tempo_converter.convert(
                self._sequential_event_to_quantized_abjad_container_converter.tempo_envelope
            )
        else:
            tempo_attachment_tuple = None
        self._tempo_attachment_tuple = tempo_attachment_tuple

        self._mutwo_lyric_to_abjad_string = mutwo_lyric_to_abjad_string

        self._write_multimeasure_rests = write_multimeasure_rests

    # ###################################################################### #
    #                          static methods                                #
    # ###################################################################### #

    @staticmethod
    def _detect_abjad_event_type(pitch_list: list[music_parameters.abc.Pitch]) -> type:
        n_pitches = len(pitch_list)
        if n_pitches == 0:
            abjad_event_type = abjad.Rest
        elif n_pitches == 1:
            abjad_event_type = abjad.Note
        else:
            abjad_event_type = abjad.Chord
        return abjad_event_type

    @staticmethod
    def _find_absolute_times_of_abjad_leaves(
        abjad_voice: abjad.Voice,
    ) -> tuple[fractions.Fraction, ...]:
        absolute_time_per_leaf_list: list[fractions.Fraction] = []
        for leaf in abjad.select(abjad_voice).leaves():
            start, _ = abjad.get.timespan(leaf).offsets
            absolute_time_per_leaf_list.append(
                fractions.Fraction(start.numerator, start.denominator)
            )
        return tuple(absolute_time_per_leaf_list)

    @staticmethod
    def _replace_rests_with_full_measure_rests(abjad_voice: abjad.Voice) -> None:
        for bar in abjad_voice:
            if all((isinstance(item, abjad.Rest) for item in bar)):
                duration = sum((item.written_duration for item in bar))
                numerator, denominator = duration.numerator, duration.denominator
                abjad.mutate.replace(
                    bar[0],
                    abjad.MultimeasureRest(
                        abjad.Duration(1, denominator), multiplier=numerator
                    ),
                    wrappers=True,
                )
                del bar[1:]

    # ###################################################################### #
    #                          private methods                               #
    # ###################################################################### #

    def _indicator_collection_to_abjad_parameters(
        self,
        indicator_collection: music_parameters.abc.IndicatorCollection,
    ) -> dict[str, abjad_parameters.abc.AbjadAttachment]:
        attachment_dict = {}
        for abjad_attachment_class in self._abjad_attachment_class_sequence:
            abjad_attachment = abjad_attachment_class.from_indicator_collection(
                indicator_collection
            )
            if abjad_attachment:
                attachment_dict.update(
                    {abjad_attachment_class.get_class_name(): abjad_attachment}
                )

        return attachment_dict

    def _grace_note_sequential_event_to_abjad_attachment(
        self,
        grace_note_sequential_event_or_after_grace_note_sequential_event: core_events.SequentialEvent[
            core_events.SimpleEvent
        ],
        is_before: bool,
    ) -> dict[str, abjad_parameters.abc.AbjadAttachment]:
        if not grace_note_sequential_event_or_after_grace_note_sequential_event:
            return {}
        converter = _GraceNotesToAbjadVoiceConverter(
            is_before,
            self._simple_event_to_pitch_list,
            self._simple_event_to_volume,
            self._simple_event_to_playing_indicator_collection,
            self._simple_event_to_notation_indicator_collection,
            self._is_simple_event_rest,
            self._mutwo_pitch_to_abjad_pitch_converter,
        )
        grace_note_sequential_event_container = converter.convert(
            grace_note_sequential_event_or_after_grace_note_sequential_event
        )
        if is_before:
            name = "grace_note_sequential_event"
            abjad_attachment_class = abjad_parameters.GraceNoteSequentialEvent
        else:
            name = "after_grace_note_sequential_event"
            abjad_attachment_class = abjad_parameters.AfterGraceNoteSequentialEvent
        return {name: abjad_attachment_class(grace_note_sequential_event_container)}

    def _volume_to_abjad_attachment(
        self, volume: music_parameters.abc.Volume
    ) -> dict[str, abjad_parameters.abc.AbjadAttachment]:
        if self._mutwo_volume_to_abjad_attachment_dynamic_converter:
            abjad_attachment_dynamic = (
                self._mutwo_volume_to_abjad_attachment_dynamic_converter.convert(volume)
            )
            if abjad_attachment_dynamic:
                return {"dynamic": abjad_attachment_dynamic}
        return {}

    def _get_tempo_attachment_tuple_for_quantized_abjad_leaves(
        self,
        abjad_voice: abjad.Voice,
    ) -> tuple[
        tuple[
            int,
            typing.Union[
                abjad_parameters.Tempo, abjad_parameters.DynamicChangeIndicationStop
            ],
        ],
        ...,
    ]:
        absolute_time_per_leaf = (
            SequentialEventToAbjadVoice._find_absolute_times_of_abjad_leaves(
                abjad_voice
            )
        )

        assert absolute_time_per_leaf == tuple(sorted(absolute_time_per_leaf))

        leaf_index_to_tempo_attachment_pairs_list: list[
            tuple[
                int,
                typing.Union[
                    abjad_parameters.Tempo,
                    abjad_parameters.DynamicChangeIndicationStop,
                ],
            ]
        ] = []
        for absolute_time, tempo_attachment in self._tempo_attachment_tuple:
            closest_leaf = core_utilities.find_closest_index(
                absolute_time, absolute_time_per_leaf
            )
            # special case:
            # check for stop dynamic change indication
            # (has to applied to the previous leaf for
            #  better looking results)
            if tempo_attachment.stop_dynamic_change_indicaton:
                leaf_index_to_tempo_attachment_pairs_list.append(
                    (closest_leaf - 1, abjad_parameters.DynamicChangeIndicationStop())
                )
            leaf_index_to_tempo_attachment_pairs_list.append(
                (closest_leaf, tempo_attachment)
            )

        return tuple(leaf_index_to_tempo_attachment_pairs_list)

    def _get_abjad_parameters_for_quantized_abjad_leaves(
        self,
        extracted_data_per_simple_event: ExtractedDataPerSimpleEvent,
    ) -> tuple[tuple[typing.Optional[abjad_parameters.abc.AbjadAttachment], ...], ...]:
        abjad_parameters_per_type_per_event: dict[
            str, list[typing.Optional[abjad_parameters.abc.AbjadAttachment]]
        ] = {
            attachment_name: [None for _ in extracted_data_per_simple_event]
            for attachment_name in self._available_attachment_tuple
        }
        for nth_event, extracted_data in enumerate(extracted_data_per_simple_event):
            (
                _,
                volume,
                grace_note_sequential_event,
                after_grace_note_sequential_event,
                playing_indicators,
                notation_indicators,
                *_,
            ) = extracted_data
            abjad_parameters_for_nth_event = self._volume_to_abjad_attachment(volume)
            abjad_parameters_for_nth_event.update(
                self._grace_note_sequential_event_to_abjad_attachment(
                    grace_note_sequential_event, True
                )
            )
            abjad_parameters_for_nth_event.update(
                self._grace_note_sequential_event_to_abjad_attachment(
                    after_grace_note_sequential_event, False
                )
            )
            abjad_parameters_for_nth_event.update(
                self._indicator_collection_to_abjad_parameters(playing_indicators)
            )
            abjad_parameters_for_nth_event.update(
                self._indicator_collection_to_abjad_parameters(notation_indicators)
            )
            for attachment_name, attachment in abjad_parameters_for_nth_event.items():
                abjad_parameters_per_type_per_event[attachment_name][
                    nth_event
                ] = attachment

        return tuple(
            tuple(abjad_parameters)
            for abjad_parameters in abjad_parameters_per_type_per_event.values()
        )

    def _apply_tempos_on_quantized_abjad_leaves(
        self,
        quanitisized_abjad_leaf_voice: abjad.Voice,
    ):
        if self._tempo_attachment_tuple:
            leaves = abjad.select(quanitisized_abjad_leaf_voice).leaves()
            tempo_attachment_data = (
                self._get_tempo_attachment_tuple_for_quantized_abjad_leaves(
                    quanitisized_abjad_leaf_voice
                )
            )
            for nth_event, tempo_attachment in tempo_attachment_data:
                tempo_attachment.process_leaf_tuple((leaves[nth_event],), None)

    def _apply_abjad_parameters_on_quantized_abjad_leaves(
        self,
        quanitisized_abjad_leaf_voice: abjad.Voice,
        related_abjad_leaf_index_tuple_tuple_per_simple_event: tuple[
            tuple[tuple[int, ...], ...], ...
        ],
        abjad_parameters_per_type_per_event_tuple: tuple[
            tuple[typing.Optional[abjad_parameters.abc.AbjadAttachment], ...], ...
        ],
    ) -> None:
        for abjad_parameters_per_type in abjad_parameters_per_type_per_event_tuple:
            previous_attachment = None
            for related_abjad_leaf_index_tuple_tuple, attachment in zip(
                related_abjad_leaf_index_tuple_tuple_per_simple_event,
                abjad_parameters_per_type,
            ):
                if attachment and attachment.is_active:
                    abjad_leaves = tuple(
                        core_utilities.get_nested_item_from_index_sequence(
                            index_tuple,
                            quanitisized_abjad_leaf_voice,
                        )
                        for index_tuple in related_abjad_leaf_index_tuple_tuple
                    )
                    processed_abjad_leaves = attachment.process_leaf_tuple(
                        abjad_leaves, previous_attachment
                    )
                    for processed_abjad_leaf, index_tuple in zip(
                        processed_abjad_leaves, related_abjad_leaf_index_tuple_tuple
                    ):
                        core_utilities.set_nested_item_from_index_sequence(
                            index_tuple,
                            quanitisized_abjad_leaf_voice,
                            processed_abjad_leaf,
                        )

                    previous_attachment = attachment

    def _extract_pitch_list_and_volume_from_simple_event(
        self, simple_event: core_events.SimpleEvent
    ) -> tuple[list[music_parameters.abc.Pitch], music_parameters.abc.Volume]:
        pitch_list = self._simple_event_to_pitch_list(simple_event)

        # TODO(Add option: no dynamic indicator if there aren't any pitches)
        if pitch_list:
            volume = self._simple_event_to_volume(simple_event)
            if not volume.amplitude:
                pitch_list = []
        else:
            volume = music_parameters.DirectVolume(0)

        return pitch_list, volume

    def _extract_data_from_simple_event(
        self, simple_event: core_events.SimpleEvent
    ) -> ExtractedData:
        # Special case for pitch_list and volume:
        # if pitch_list is empty, there is also no volume. If volume is empty
        # there is also no pitch_list.
        extracted_data = list(
            self._extract_pitch_list_and_volume_from_simple_event(simple_event)
        )

        for function in self._simple_event_to_function_tuple:
            extracted_data.append(function(simple_event))  # type: ignore

        return tuple(extracted_data)  # type: ignore

    def _apply_pitch_list_on_quantized_abjad_leaf(
        self,
        quanitisized_abjad_leaf_voice: abjad.Voice,
        abjad_pitch_list: list[abjad.Pitch],
        related_abjad_leaf_index_tuple_tuple: tuple[tuple[int, ...], ...],
    ):
        if len(abjad_pitch_list) == 1:
            leaf_class = abjad.Note
        else:
            leaf_class = abjad.Chord

        for related_abjad_leaf_index_tuple in related_abjad_leaf_index_tuple_tuple:
            abjad_leaf = core_utilities.get_nested_item_from_index_sequence(
                related_abjad_leaf_index_tuple, quanitisized_abjad_leaf_voice
            )
            if leaf_class == abjad.Note:
                # skip don't have note heads
                if hasattr(abjad_leaf, "note_head"):
                    abjad_leaf.note_head._written_pitch = abjad_pitch_list[0]

            else:
                new_abjad_leaf = leaf_class(
                    [abjad.NamedPitch() for _ in abjad_pitch_list],
                    abjad_leaf.written_duration,
                )
                for indicator in abjad.get.indicators(abjad_leaf):
                    if type(indicator) != dict:
                        abjad.attach(indicator, new_abjad_leaf)

                for abjad_pitch, note_head in zip(
                    abjad_pitch_list, new_abjad_leaf.note_heads
                ):
                    note_head._written_pitch = abjad_pitch

                core_utilities.set_nested_item_from_index_sequence(
                    related_abjad_leaf_index_tuple,
                    quanitisized_abjad_leaf_voice,
                    new_abjad_leaf,
                )

    def _apply_pitches_on_quantized_abjad_leaves(
        self,
        quanitisized_abjad_leaf_voice: abjad.Voice,
        related_abjad_leaf_index_tuple_tuple_per_simple_event: tuple[
            tuple[tuple[int, ...], ...], ...
        ],
        extracted_data_per_simple_event: ExtractedDataPerSimpleEvent,
        is_simple_event_rest_per_simple_event: tuple[bool, ...],
    ):
        for (
            is_simple_event_rest,
            extracted_data,
            related_abjad_leaf_index_tuple_tuple,
        ) in zip(
            is_simple_event_rest_per_simple_event,
            extracted_data_per_simple_event,
            related_abjad_leaf_index_tuple_tuple_per_simple_event,
        ):
            if not is_simple_event_rest:
                pitch_list = extracted_data[0]
                abjad_pitch_list = [
                    self._mutwo_pitch_to_abjad_pitch_converter.convert(pitch)
                    for pitch in pitch_list
                ]
                self._apply_pitch_list_on_quantized_abjad_leaf(
                    quanitisized_abjad_leaf_voice,
                    abjad_pitch_list,
                    related_abjad_leaf_index_tuple_tuple,
                )

    def _get_lyric_content(
        self, extracted_data_per_simple_event: ExtractedDataPerSimpleEvent
    ) -> str:
        lyric_content_list = []
        for extracted_data in extracted_data_per_simple_event:
            lyric = extracted_data[6]
            abjad_string = self._mutwo_lyric_to_abjad_string(lyric)
            lyric_content_list.append(abjad_string)
        return " ".join(lyric_content_list)

    def _apply_lyrics_on_voice(
        self, voice_to_apply_lyrics_to: abjad.Voice, lyric_content: str
    ):
        # We only add the lyrics in case it isn't empty
        reduced_lyric = tuple(set(filter(bool, lyric_content.split(" "))))
        test_tuple = (
            # "" -> this doesn't need to be added
            bool(lyric_content),
            # "        " -> this doesn't need to be added
            not lyric_content.isspace(),
            # "_ _ _ _" -> this doesn't need to be added
            len(reduced_lyric) != 1 or reduced_lyric[0] != "_",
        )
        if all(test_tuple):
            abjad.attach(
                abjad.LilyPondLiteral(
                    "\\addlyrics { " + lyric_content + " }",
                    format_slot="absolute_after",
                ),
                voice_to_apply_lyrics_to,
            )

    def _quantize_sequential_event(
        self,
        sequential_event_to_convert: core_events.SequentialEvent[
            core_events.SimpleEvent
        ],
        is_simple_event_rest_per_simple_event: tuple[bool, ...],
    ) -> tuple[abjad.Container, tuple[tuple[tuple[int, ...], ...], ...],]:
        is_simple_event_rest_per_simple_event_iterator = iter(
            is_simple_event_rest_per_simple_event
        )
        (
            quanitisized_abjad_leaf_voice,
            related_abjad_leaf_index_tuple_tuple_per_simple_event,
        ) = self._sequential_event_to_quantized_abjad_container_converter.convert(
            sequential_event_to_convert.set_parameter(  # type: ignore
                "is_rest",
                lambda _: next(is_simple_event_rest_per_simple_event_iterator),
                set_unassigned_parameter=True,
                mutate=False,  # type: ignore
            )
        )
        return (
            quanitisized_abjad_leaf_voice,
            related_abjad_leaf_index_tuple_tuple_per_simple_event,
        )

    def _fill_abjad_container(
        self,
        abjad_container_to_fill: abjad.Voice,
        sequential_event_to_convert: core_events.SequentialEvent[
            core_events.SimpleEvent
        ],
    ):
        # tie rests before processing the event!
        sequential_event_to_convert = sequential_event_to_convert.tie_by(
            lambda event0, event1: self._is_simple_event_rest(event0)
            and self._is_simple_event_rest(event1),
            event_type_to_examine=core_events.SimpleEvent,
            mutate=False,  # type: ignore
        )

        # first, extract data from simple events and find rests
        extracted_data_per_simple_event = tuple(
            self._extract_data_from_simple_event(simple_event)
            for simple_event in sequential_event_to_convert
        )
        is_simple_event_rest_per_simple_event = tuple(
            self._is_simple_event_rest(simple_event)
            for simple_event in sequential_event_to_convert
        )

        # second, quantize the sequential event
        (
            quanitisized_abjad_leaf_voice,
            related_abjad_leaf_index_tuple_tuple_per_simple_event,
        ) = self._quantize_sequential_event(
            sequential_event_to_convert, is_simple_event_rest_per_simple_event
        )

        # third, apply pitches on Abjad voice
        self._apply_pitches_on_quantized_abjad_leaves(
            quanitisized_abjad_leaf_voice,
            related_abjad_leaf_index_tuple_tuple_per_simple_event,
            extracted_data_per_simple_event,
            is_simple_event_rest_per_simple_event,
        )

        # fourth, apply dynamics, tempos and playing_indicators on abjad voice
        abjad_parameters_per_type_per_event = (
            self._get_abjad_parameters_for_quantized_abjad_leaves(
                extracted_data_per_simple_event
            )
        )
        self._apply_tempos_on_quantized_abjad_leaves(quanitisized_abjad_leaf_voice)
        self._apply_abjad_parameters_on_quantized_abjad_leaves(
            quanitisized_abjad_leaf_voice,
            related_abjad_leaf_index_tuple_tuple_per_simple_event,
            abjad_parameters_per_type_per_event,
        )

        # fifth, replace rests lasting one bar with full measure rests
        if self._write_multimeasure_rests:
            SequentialEventToAbjadVoice._replace_rests_with_full_measure_rests(
                quanitisized_abjad_leaf_voice
            )

        # move leaves from 'quanitisized_abjad_leaf_voice' object to target container
        abjad.mutate.swap(quanitisized_abjad_leaf_voice, abjad_container_to_fill)

        # finally: apply lyrics on abjad voice
        lyric_content = self._get_lyric_content(extracted_data_per_simple_event)
        self._apply_lyrics_on_voice(abjad_container_to_fill, lyric_content)

    # ###################################################################### #
    #               public methods for interaction with the user             #
    # ###################################################################### #

    def convert(
        self,
        sequential_event_to_convert: core_events.SequentialEvent[
            core_events.SimpleEvent
        ],
    ) -> abjad.Voice:
        """Convert passed :class:`~mutwo.core_events.SequentialEvent`.

        :param sequential_event_to_convert: The
            :class:`~mutwo.core_events.SequentialEvent` which shall
            be converted to the :class:`abjad.Voice` object.
        :type sequential_event_to_convert: mutwo.core_events.SequentialEvent

        **Example:**

        >>> import abjad
        >>> from mutwo.events import basic, music
        >>> from mutwo.converters.frontends import abjad as mutwo_abjad
        >>> mutwo_melody = basic.SequentialEvent(
        >>>     [
        >>>         music.NoteLike(pitch, duration)
        >>>         for pitch, duration in zip("c a g e".split(" "), (1, 1 / 6, 1 / 6, 1 / 6))
        >>>     ]
        >>> )
        >>> converter = mutwo_abjad.SequentialEventToAbjadVoice()
        >>> abjad_melody = converter.convert(mutwo_melody)
        >>> abjad.lilypond(abjad_melody)
        \\new Voice
        {
            {
                \\tempo 4=120
                %%% \\time 4/4 %%%
                c'1
                \\mf
            }
            {
                \\times 2/3 {
                    a'4
                    g'4
                    e'4
                }
                r2
            }
        }
        """

        return super().convert(sequential_event_to_convert)


class _GraceNotesToAbjadVoiceConverter(SequentialEventToAbjadVoice):
    class GraceNotesToQuantizedAbjadContainerConverter(core_converters.abc.Converter):
        def convert(
            self, sequential_event_to_convert: core_events.SequentialEvent
        ) -> abjad.Container:
            container = abjad.Container([], simultaneous=False)
            indices = []
            for nth_event, event in enumerate(sequential_event_to_convert):
                leaf = abjad.Note("c", event.duration)
                container.append(leaf)
                indices.append(((nth_event,),))
            return container, tuple(indices)

    def __init__(
        self,
        is_before: bool,
        simple_event_to_pitch_list: typing.Callable[
            [core_events.SimpleEvent], list[music_parameters.abc.Pitch]
        ],
        simple_event_to_volume: typing.Callable[
            [core_events.SimpleEvent], music_parameters.abc.Volume
        ],
        simple_event_to_playing_indicator_collection: typing.Callable[
            [core_events.SimpleEvent],
            music_parameters.PlayingIndicatorCollection,
        ],
        simple_event_to_notation_indicator_collection: typing.Callable[
            [core_events.SimpleEvent],
            music_parameters.NotationIndicatorCollection,
        ],
        is_simple_event_rest: typing.Callable[[core_events.SimpleEvent], bool],
        mutwo_pitch_to_abjad_pitch_converter: MutwoPitchToAbjadPitch,
    ):
        def raise_attribute_error(_):
            raise AttributeError

        if is_before:
            abjad_container_class = abjad.BeforeGraceContainer
        else:
            abjad_container_class = abjad.AfterGraceContainer

        super().__init__(
            sequential_event_to_quantized_abjad_container_converter=self.GraceNotesToQuantizedAbjadContainerConverter(),
            simple_event_to_pitch_list=simple_event_to_pitch_list,
            simple_event_to_volume=simple_event_to_volume,
            simple_event_to_playing_indicator_collection=simple_event_to_playing_indicator_collection,
            simple_event_to_notation_indicator_collection=simple_event_to_notation_indicator_collection,
            is_simple_event_rest=is_simple_event_rest,
            mutwo_pitch_to_abjad_pitch_converter=mutwo_pitch_to_abjad_pitch_converter,
            mutwo_volume_to_abjad_attachment_dynamic_converter=None,
            tempo_envelope_to_abjad_attachment_tempo_converter=None,
            simple_event_to_grace_note_sequential_event=lambda _: core_events.SequentialEvent(
                []
            ),
            simple_event_to_after_grace_note_sequential_event=lambda _: core_events.SequentialEvent(
                []
            ),
            write_multimeasure_rests=False,
            abjad_container_class=abjad_container_class,
            lilypond_type_of_abjad_container=None,
        )

    def _grace_note_sequential_event_to_abjad_attachment(
        self,
        grace_note_sequential_event_or_after_grace_note_sequential_event: core_events.SequentialEvent[
            core_events.SimpleEvent
        ],
        is_before: bool,
    ) -> dict[str, abjad_parameters.abc.AbjadAttachment]:
        return {}

    def _get_tempo_attachment_tuple_for_quantized_abjad_leaves(
        self,
        abjad_voice: abjad.Voice,
    ) -> tuple[
        tuple[
            int,
            typing.Union[
                abjad_parameters.Tempo, abjad_parameters.DynamicChangeIndicationStop
            ],
        ],
        ...,
    ]:
        return tuple([])


class NestedComplexEventToComplexEventToAbjadContainers(core_converters.abc.Converter):
    @abc.abstractmethod
    def convert(
        self, nested_complex_event_to_convert: core_events.abc.ComplexEvent
    ) -> tuple[ComplexEventToAbjadContainer, ...]:
        raise NotImplementedError


class CycleBasedNestedComplexEventToComplexEventToAbjadContainers(
    NestedComplexEventToComplexEventToAbjadContainers
):
    def __init__(
        self,
        complex_event_to_abjad_container_converter_sequence: typing.Sequence[
            ComplexEventToAbjadContainer
        ],
    ):
        self._complex_event_to_abjad_container_converters = (
            complex_event_to_abjad_container_converter_sequence
        )

    def convert(
        self, nested_complex_event_to_convert: core_events.abc.ComplexEvent
    ) -> tuple[ComplexEventToAbjadContainer, ...]:
        complex_event_to_abjad_container_converters_cycle = itertools.cycle(
            self._complex_event_to_abjad_container_converters
        )
        complex_event_to_abjad_container_converter_list = []
        for _ in nested_complex_event_to_convert:
            complex_event_to_abjad_container_converter_list.append(
                next(complex_event_to_abjad_container_converters_cycle)
            )
        return tuple(complex_event_to_abjad_container_converter_list)


class TagBasedNestedComplexEventToComplexEventToAbjadContainers(
    NestedComplexEventToComplexEventToAbjadContainers
):
    def __init__(
        self,
        tag_to_complex_event_to_abjad_container_converter: dict[
            str, ComplexEventToAbjadContainer
        ],
        complex_event_to_tag: typing.Callable[
            [core_events.abc.ComplexEvent], str
        ] = lambda complex_event: complex_event.tag,
    ):
        self._tag_to_complex_event_to_abjad_container_converter = (
            tag_to_complex_event_to_abjad_container_converter
        )
        self._complex_event_to_tag = complex_event_to_tag

    def convert(
        self, nested_complex_event_to_convert: core_events.abc.ComplexEvent
    ) -> tuple[ComplexEventToAbjadContainer, ...]:
        complex_event_to_abjad_container_converter_list = []
        for complex_event in nested_complex_event_to_convert:
            tag = self._complex_event_to_tag(complex_event)
            try:
                complex_event_to_abjad_container_converter = (
                    self._tag_to_complex_event_to_abjad_container_converter[tag]
                )
            except KeyError:
                raise KeyError(
                    f"Found undefined tag '{tag}'."
                    " This object only knows the following tags:"
                    f" '{self._tag_to_complex_event_to_abjad_container_converter.keys()}'"
                )

            complex_event_to_abjad_container_converter_list.append(
                complex_event_to_abjad_container_converter
            )
        return tuple(complex_event_to_abjad_container_converter_list)


class NestedComplexEventToAbjadContainer(ComplexEventToAbjadContainer):
    def __init__(
        self,
        nested_complex_event_to_complex_event_to_abjad_container_converters_converter: NestedComplexEventToComplexEventToAbjadContainers,
        abjad_container_class: typing.Type[abjad.Container],
        lilypond_type_of_abjad_container: str,
        complex_event_to_abjad_container_name: typing.Callable[
            [core_events.abc.ComplexEvent], str
        ] = lambda complex_event: complex_event.tag,
        pre_process_abjad_container_routine_sequence: typing.Sequence[
            abjad_converters.ProcessAbjadContainerRoutine
        ] = tuple([]),
        post_process_abjad_container_routine_sequence: typing.Sequence[
            abjad_converters.ProcessAbjadContainerRoutine
        ] = tuple([]),
    ):
        super().__init__(
            abjad_container_class,
            lilypond_type_of_abjad_container,
            complex_event_to_abjad_container_name,
            pre_process_abjad_container_routine_sequence,
            post_process_abjad_container_routine_sequence,
        )
        self._nested_complex_event_to_complex_event_to_abjad_container_converters_converter = nested_complex_event_to_complex_event_to_abjad_container_converters_converter

    def _fill_abjad_container(
        self,
        abjad_container_to_fill: abjad.Container,
        nested_complex_event_to_convert: core_events.abc.ComplexEvent,
    ):
        complex_event_to_abjad_container_converter_tuple = self._nested_complex_event_to_complex_event_to_abjad_container_converters_converter.convert(
            nested_complex_event_to_convert
        )
        for complex_event, complex_event_to_abjad_container_converter in zip(
            nested_complex_event_to_convert,
            complex_event_to_abjad_container_converter_tuple,
        ):
            converted_complex_event = (
                complex_event_to_abjad_container_converter.convert(complex_event)
            )
            abjad_container_to_fill.append(converted_complex_event)
