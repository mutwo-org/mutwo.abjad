"""Module to quantize free :class:`SequentialEvent` to notation based abjad :class:`Container`"""

import abc
import typing
import warnings

try:
    import quicktions as fractions  # type: ignore
except ImportError:
    import fractions  # type: ignore

import abjad  # type: ignore
from abjadext import nauert  # type: ignore
import ranges  # type: ignore

from mutwo import core_converters
from mutwo import core_events
from mutwo import core_parameters
from mutwo import core_utilities

__all__ = (
    "SequentialEventToQuantizedAbjadContainer",
    "NauertSequentialEventToQuantizedAbjadContainer",
    "NauertSequentialEventToDurationLineBasedQuantizedAbjadContainer",
    "LeafMakerSequentialEventToQuantizedAbjadContainer",
    "LeafMakerSequentialEventToDurationLineBasedQuantizedAbjadContainer",
)


class NoTimeSignatureError(Exception):
    pass


class SequentialEventToQuantizedAbjadContainer(core_converters.abc.Converter):
    """Quantize :class:`~mutwo.core_events.SequentialEvent` objects.

    :param time_signature_sequence: Set time signatures to divide the quantized abjad data
        in desired bar sizes. If the converted :class:`~mutwo.core_events.SequentialEvent`
        is longer than the sum of all passed time signatures, the last time signature
        will be repeated for the remaining bars.
    :param tempo_envelope: Defines the tempo of the converted music. This is an
        :class:`core_events.TempoEnvelope` object which durations are beats and which
        levels are either numbers (that will be interpreted as beats per minute ('BPM'))
        or :class:`~mutwo.core_parameters.abc.TempoPoint` objects. If no tempo envelope has
        been defined, Mutwo will assume a constant tempo of 1/4 = 120 BPM.
    """

    def __init__(
        self,
        time_signature_sequence: typing.Sequence[abjad.TimeSignature] = (
            abjad.TimeSignature((4, 4)),
        ),
        tempo_envelope: core_events.TempoEnvelope = None,
    ):
        n_time_signature_sequence = len(time_signature_sequence)
        if n_time_signature_sequence == 0:
            raise NoTimeSignatureError(
                "Found empty sequence for argument 'time_signature_sequence'. Specify at least"
                " one time signature!"
            )

        time_signature_tuple = tuple(time_signature_sequence)
        if tempo_envelope is None:
            tempo_envelope = core_events.TempoEnvelope(
                (
                    (0, core_parameters.DirectTempoPoint(120)),
                    (0, core_parameters.DirectTempoPoint(120)),
                )
            )

        self._time_signature_tuple = time_signature_tuple
        self._tempo_envelope = tempo_envelope

    @property
    def tempo_envelope(self) -> core_events.TempoEnvelope:
        return self._tempo_envelope

    # ###################################################################### #
    #               public methods for interaction with the user             #
    # ###################################################################### #

    @abc.abstractmethod
    def convert(
        self, sequential_event_to_convert: core_events.SequentialEvent
    ) -> tuple[abjad.Container, tuple[tuple[tuple[int, ...], ...], ...]]:
        raise NotImplementedError


class NauertSequentialEventToQuantizedAbjadContainer(
    SequentialEventToQuantizedAbjadContainer
):
    """Quantize :class:`~mutwo.core_events.SequentialEvent` objects via :mod:`abjadext.nauert`.

    :param time_signature_sequence: Set time signatures to divide the quantized abjad data
        in desired bar sizes. If the converted :class:`~mutwo.core_events.SequentialEvent`
        is longer than the sum of all passed time signatures, the last time signature
        will be repeated for the remaining bars.
    :param duration_unit: This defines the `duration_unit` of the passed
        :class:`~mutwo.core_events.SequentialEvent` (how the
        :attr:`~mutwo.events.abc.Event.duration` attribute will be
        interpreted). Can either be 'beats' (default) or 'miliseconds'.
        WARNING: 'miliseconds' isn't working properly yet!
    :param tempo_envelope: Defines the tempo of the converted music. This is an
        :class:`core_events.TempoEnvelope` object which durations are beats and which
        levels are either numbers (that will be interpreted as beats per minute ('BPM'))
        or :class:`~mutwo.core_parameters.abc.TempoPoint` objects. If no tempo envelope has
        been defined, Mutwo will assume a constant tempo of 1/4 = 120 BPM.
    :param attack_point_optimizer: Optionally the user can pass a
        :class:`nauert.AttackPointOptimizer` object. Attack point optimizer help to
        split events and tie them for better looking notation. The default attack point
        optimizer is :class:`nauert.MeasurewiseAttackPointOptimizer` which splits events
        to better represent metrical structures within bars. If no optimizer is desired
        this argument can be set to ``None``.

    Unlike :class:`LeafMakerSequentialEventToQuantizedAbjadContainer` this converter
    supports nested tuplets and ties across tuplets. But this converter is much slower
    than the :class:`LeafMakerSequentialEventToQuantizedAbjadContainer`. Because the
    converter depends on the abjad extension `nauert` its quality is dependent on the
    inner mechanism of the used package. Because the quantization made by the `nauert`
    package can be somewhat indeterministic a lot of tweaking may be necessary for
    complex musical structures.
    """

    # TODO(add proper miliseconds conversion: you will have to add the tempo_envelope
    # when building the QEventSequence. Furthermore you should auto write down the
    # metronome marks when initialising from miliseconds?)

    def __init__(
        self,
        time_signature_sequence: typing.Sequence[abjad.TimeSignature] = (
            abjad.TimeSignature((4, 4)),
        ),
        duration_unit: str = "beats",  # for future: typing.Literal["beats", "miliseconds"]
        tempo_envelope: core_events.TempoEnvelope = None,
        attack_point_optimizer: typing.Optional[
            nauert.AttackPointOptimizer
        ] = nauert.MeasurewiseAttackPointOptimizer(),
        search_tree: typing.Optional[nauert.SearchTree] = None,
    ):
        if duration_unit == "miliseconds":
            # warning for not well implemented miliseconds conversion

            message = (
                "The current implementation can't apply tempo changes for duration unit"
                " 'miliseconds' yet! Furthermore to quantize via duration_unit"
                " 'miliseconds' isn't well tested yet and may return unexpected"
                " results."
            )
            warnings.warn(message)

        time_signature_tuple = tuple(time_signature_sequence)
        # nauert will raise an error if there is only one time signature
        if len(time_signature_tuple) == 1:
            time_signature_tuple += time_signature_tuple

        super().__init__(time_signature_tuple, tempo_envelope)

        self._duration_unit = duration_unit
        self._attack_point_optimizer = attack_point_optimizer
        self._q_schema = NauertSequentialEventToQuantizedAbjadContainer._make_q_schema(
            self._time_signature_tuple, search_tree
        )

    # ###################################################################### #
    #                          static methods                                #
    # ###################################################################### #

    @staticmethod
    def _get_respective_q_event_from_abjad_leaf(
        abjad_leaf: typing.Union[abjad.Rest, abjad.Note]
    ) -> typing.Optional[nauert.QEvent]:
        # TODO(improve ugly, heuristic, unreliable code)
        try:
            return abjad.get.indicators(abjad_leaf)[0]["q_events"][0]
        except TypeError:
            return None
        except KeyError:
            return None
        except IndexError:
            return None

    @staticmethod
    def _process_abjad_leaf(
        indices: list[int],
        abjad_leaf: abjad.Leaf,
        related_abjad_leaves_per_simple_event: list[list[tuple[int, ...]]],
        q_event_sequence: nauert.QEventSequence,
        has_tie: bool,
        index_of_previous_q_event: int,
    ) -> tuple[bool, int]:
        q_event = NauertSequentialEventToQuantizedAbjadContainer._get_respective_q_event_from_abjad_leaf(
            abjad_leaf
        )

        if q_event and type(q_event) != nauert.TerminalQEvent:
            nth_q_event = q_event_sequence.sequence.index(q_event)
            related_abjad_leaves_per_simple_event[nth_q_event].append(tuple(indices))
            index_of_previous_q_event = nth_q_event
        elif has_tie:
            related_abjad_leaves_per_simple_event[index_of_previous_q_event].append(
                tuple(indices)
            )
        # skip leaves without any links
        # else:
        #     related_abjad_leaves_per_simple_event.append([tuple(indices)])

        has_tie = abjad.get.has_indicator(abjad_leaf, abjad.Tie)

        return has_tie, index_of_previous_q_event

    @staticmethod
    def _process_tuplet(
        indices: list[int],
        tuplet: abjad.Tuplet,
        related_abjad_leaves_per_simple_event: list[list[tuple[int, ...]]],
        q_event_sequence: nauert.QEventSequence,
        has_tie: bool,
        index_of_previous_q_event: int,
    ) -> tuple[bool, int]:
        for (
            nth_abjad_leaf_or_tuplet,
            abjad_leaf_or_tuplet,
        ) in enumerate(tuplet):
            (
                has_tie,
                index_of_previous_q_event,
            ) = NauertSequentialEventToQuantizedAbjadContainer._process_abjad_leaf_or_tuplet(
                indices + [nth_abjad_leaf_or_tuplet],
                abjad_leaf_or_tuplet,
                related_abjad_leaves_per_simple_event,
                q_event_sequence,
                has_tie,
                index_of_previous_q_event,
            )

        return has_tie, index_of_previous_q_event

    @staticmethod
    def _process_abjad_leaf_or_tuplet(
        index_list: list[int],
        abjad_leaf_or_tuplet: typing.Union[abjad.Tuplet, abjad.Leaf],
        related_abjad_leaves_per_simple_event: list[list[tuple[int, ...]]],
        q_event_sequence: nauert.QEventSequence,
        has_tie: bool,
        index_of_previous_q_event: int,
    ) -> tuple[bool, int]:
        if isinstance(abjad_leaf_or_tuplet, abjad.Tuplet):
            return NauertSequentialEventToQuantizedAbjadContainer._process_tuplet(
                index_list,
                abjad_leaf_or_tuplet,
                related_abjad_leaves_per_simple_event,
                q_event_sequence,
                has_tie,
                index_of_previous_q_event,
            )

        else:
            return NauertSequentialEventToQuantizedAbjadContainer._process_abjad_leaf(
                index_list,
                abjad_leaf_or_tuplet,
                related_abjad_leaves_per_simple_event,
                q_event_sequence,
                has_tie,
                index_of_previous_q_event,
            )

    @staticmethod
    def _make_related_abjad_leaves_per_simple_event(
        sequential_event: core_events.SequentialEvent,
        q_event_sequence: nauert.QEventSequence,
        quanitisized_abjad_leaf_voice: abjad.Voice,
    ) -> tuple[tuple[tuple[int, ...], ...], ...,]:
        has_tie = False
        index_of_previous_q_event: int = 0
        related_abjad_leaves_per_simple_event: list[list[tuple[int, ...]]] = [
            [] for _ in sequential_event
        ]
        for nth_bar, bar in enumerate(quanitisized_abjad_leaf_voice):
            for nth_abjad_leaf_or_tuplet, abjad_leaf_or_tuplet in enumerate(bar):
                (
                    has_tie,
                    index_of_previous_q_event,
                ) = NauertSequentialEventToQuantizedAbjadContainer._process_abjad_leaf_or_tuplet(
                    [nth_bar, nth_abjad_leaf_or_tuplet],
                    abjad_leaf_or_tuplet,
                    related_abjad_leaves_per_simple_event,
                    q_event_sequence,
                    has_tie,
                    index_of_previous_q_event,
                )

        return tuple(
            tuple(tuple(item) for item in pair)
            for pair in related_abjad_leaves_per_simple_event
        )

    @staticmethod
    def _make_q_schema(
        time_signature_tuple: tuple[abjad.TimeSignature, ...],
        search_tree: typing.Optional[nauert.SearchTree],
    ) -> nauert.QSchema:
        formated_time_signature_list = []
        for time_signature in time_signature_tuple:
            formated_time_signature_list.append({"time_signature": time_signature})

        keyword_arguments = {
            "use_full_measure": True,
            "tempo": abjad.MetronomeMark((1, 4), 60),
        }

        if search_tree:
            keyword_arguments.update({"search_tree": search_tree})

        return nauert.MeasurewiseQSchema(
            *formated_time_signature_list, **keyword_arguments
        )

    # ###################################################################### #
    #                         private methods                                #
    # ###################################################################### #

    def _sequential_event_to_q_event_sequence(
        self, sequential_event: core_events.SequentialEvent
    ) -> nauert.QEventSequence:
        duration_list = list(sequential_event.get_parameter("duration"))

        for nth_simple_event, simple_event in enumerate(sequential_event):
            if simple_event.is_rest:
                duration_list[nth_simple_event] = (
                    core_parameters.DirectDuration(0) - duration_list[nth_simple_event]
                )

        if self._duration_unit == "beats":
            return nauert.QEventSequence.from_tempo_scaled_durations(
                duration_list, tempo=abjad.MetronomeMark((1, 4), 60)
            )

        elif self._duration_unit == "miliseconds":
            return nauert.QEventSequence.from_millisecond_durations(duration_list)

        else:
            message = (
                "Unknown duration unit '{}'. Use duration unit 'beats' or"
                " 'miliseconds'.".format(self._duration_unit)
            )
            raise NotImplementedError(message)

    def _q_event_sequence_to_quanitisized_abjad_leaf_voice(
        self, q_event_sequence: nauert.QEventSequence
    ) -> abjad.Voice:
        quantizer = nauert.Quantizer()
        return quantizer(
            q_event_sequence,
            q_schema=self._q_schema,
            attach_tempos=True if self._duration_unit == "miliseconds" else False,
            attack_point_optimizer=self._attack_point_optimizer,
        )

    # ###################################################################### #
    #               public methods for interaction with the user             #
    # ###################################################################### #

    def convert(
        self, sequential_event_to_convert: core_events.SequentialEvent
    ) -> tuple[abjad.Container, tuple[tuple[tuple[int, ...], ...], ...],]:
        q_event_sequence = self._sequential_event_to_q_event_sequence(
            sequential_event_to_convert
        )
        quanitisized_abjad_leaf_voice = (
            self._q_event_sequence_to_quanitisized_abjad_leaf_voice(q_event_sequence)
        )

        related_abjad_leaves_per_simple_event = NauertSequentialEventToQuantizedAbjadContainer._make_related_abjad_leaves_per_simple_event(
            sequential_event_to_convert, q_event_sequence, quanitisized_abjad_leaf_voice
        )
        return (
            quanitisized_abjad_leaf_voice,
            related_abjad_leaves_per_simple_event,
        )


class LeafMakerSequentialEventToQuantizedAbjadContainer(
    SequentialEventToQuantizedAbjadContainer
):
    """Quantize :class:`~mutwo.core_events.SequentialEvent` object via :mod:`abjad.LeafMaker`.

    :param time_signature_sequence: Set time signatures to divide the quantized abjad data
        in desired bar sizes. If the converted
        :class:`~mutwo.core_events.SequentialEvent` is longer than the sum of
        all passed time signatures, the last time signature
        will be repeated for the remaining bars.
    :param tempo_envelope: Defines the tempo of the converted music. This is an
        :class:`core_events.TempoEnvelope` object which durations are beats and which
        levels are either numbers (that will be interpreted as beats per minute ('BPM'))
        or :class:`~mutwo.core_parameters.abc.TempoPoint` objects. If no tempo envelope
        has been defined, Mutwo will assume a constant tempo of 1/4 = 120 BPM.

    This method is significantly faster than the
    :class:`NauertSequentialEventToQuantizedAbjadContainer`. But it also
    has several known limitations:

        1. :class:`LeafMakerSequentialEventToQuantizedAbjadContainer` doesn't
           support nested tuplets.
        2. :class:`LeafMakerSequentialEventToQuantizedAbjadContainer` doesn't
           support ties across tuplets with different prolation (or across tuplets
           and not-tuplet notation). If ties are desired the user has to build them
           manually before passing the :class:`~mutwo.core_events.SequentialEvent`
           to the converter.
    """

    _maximum_dot_count = 1

    def __init__(
        self, *args, do_rewrite_meter: bool = True, add_beams: bool = True, **kwargs
    ):
        self._leaf_maker = abjad.LeafMaker(
            forbidden_note_duration=abjad.Duration(8, 1),
            forbidden_rest_duration=abjad.Duration(8, 1),
        )
        super().__init__(*args, **kwargs)
        self._do_rewrite_meter = do_rewrite_meter
        self._add_beams = add_beams

    # ###################################################################### #
    #                       static private methods                           #
    # ###################################################################### #

    @staticmethod
    def _find_offset_inventory(meter: abjad.Meter) -> tuple[abjad.Offset, ...]:
        for nth_offset_inventory, offset_inventory in enumerate(
            depthwise_offset_inventory := meter.depthwise_offset_inventory
        ):
            difference = offset_inventory[1] - offset_inventory[0]
            if difference == fractions.Fraction(1, 4):
                return offset_inventory
            elif difference <= fractions.Fraction(1, 4):
                return depthwise_offset_inventory[nth_offset_inventory - 1]
        return offset_inventory

    @staticmethod
    def _add_explicit_beams(
        bar: abjad.Container, meter: abjad.Meter, global_offset: abjad.Offset
    ) -> None:
        offset_inventory = (
            LeafMakerSequentialEventToQuantizedAbjadContainer._find_offset_inventory(
                meter
            )
        )
        leaf_offset_list = []
        # don't attach beams on tuplets
        relevant_bar_items = filter(
            lambda leaf_or_tuplet: isinstance(leaf_or_tuplet, abjad.Leaf)
            and leaf_or_tuplet.written_duration < fractions.Fraction(1, 4),
            bar,
        )
        leaf_selection = abjad.select.leaves(relevant_bar_items)
        for leaf in leaf_selection:
            offset = abjad.get.timespan(leaf).start_offset - global_offset
            leaf_offset_list.append(offset)

        beam_range_list = []
        for start, end in zip(offset_inventory, offset_inventory[1:]):
            area = ranges.Range(start, end)
            offset_tuple = tuple(
                filter(lambda offset: offset in area, leaf_offset_list)
            )
            n_elements = len(offset_tuple)
            is_start_in_leaves = start in offset_tuple

            # make new beam range
            if is_start_in_leaves and n_elements > 1:
                new_beam_range = [
                    leaf_offset_list.index(offset_tuple[0]),
                    leaf_offset_list.index(offset_tuple[-1]),
                ]
                beam_range_list.append(new_beam_range)

        for beam_range in beam_range_list:
            start, stop = beam_range
            abjad.attach(abjad.StartBeam(), leaf_selection[start])
            abjad.attach(abjad.StopBeam(), leaf_selection[stop])

        global_offset += offset_inventory[-1]
        return global_offset

    @staticmethod
    def _find_tuplet_indices(bar: abjad.Container) -> tuple[int, ...]:
        tuplet_index_list = []
        for index, leaf_or_tuplet in enumerate(bar):
            if isinstance(leaf_or_tuplet, abjad.Tuplet):
                tuplet_index_list.append(index)

        return tuple(tuplet_index_list)

    @staticmethod
    def _group_tuplet_indices(tuplet_index_tuple: tuple[int, ...]) -> list[list[int]]:
        """Put adjacent tuplet indices into groups."""

        grouped_tuplet_index_list = [[]]
        last_tuplet_index = None
        for tuplet_index in tuplet_index_tuple:
            if last_tuplet_index:
                difference = tuplet_index - last_tuplet_index
                if difference == 1:
                    grouped_tuplet_index_list[-1].append(tuplet_index)
                else:
                    grouped_tuplet_index_list.append([tuplet_index])
            else:
                grouped_tuplet_index_list[-1].append(tuplet_index)
            last_tuplet_index = tuplet_index
        return grouped_tuplet_index_list

    @staticmethod
    def _concatenate_adjacent_tuplets_for_one_group(
        bar: abjad.Container, group: list[int]
    ):
        implied_prolation_list = [bar[index].implied_prolation for index in group]
        common_prolation_group_list = [[implied_prolation_list[0], [group[0]]]]
        for index, prolation in zip(group[1:], implied_prolation_list[1:]):
            if prolation == common_prolation_group_list[-1][0]:
                common_prolation_group_list[-1][1].append(index)
            else:
                common_prolation_group_list.append([prolation, [index]])

        tuplet_list = []
        for prolation, tuplet_index_list in common_prolation_group_list:
            tuplet = abjad.Tuplet(prolation)
            for tuplet_index in tuplet_index_list:
                for component in bar[tuplet_index]:
                    tuplet.append(abjad.mutate.copy(component))
            tuplet_list.append(tuplet)

        bar[group[0] : group[-1] + 1] = tuplet_list

    # ###################################################################### #
    #                       private methods                                  #
    # ###################################################################### #

    def _make_note_tuple(
        self, sequential_event_to_convert: core_events.SequentialEvent
    ) -> tuple[abjad.Leaf, ...]:
        pitch_list = [
            None if event.is_rest else "c" for event in sequential_event_to_convert
        ]
        # It has to be a list! Otherwise abjad will raise an exception.
        duration_list = list(
            map(
                lambda duration: abjad.Duration(duration),
                sequential_event_to_convert.get_parameter("duration"),
            )
        )
        note_tuple = tuple(self._leaf_maker(pitch_list, duration_list))
        return note_tuple

    def _concatenate_adjacent_tuplets_for_one_bar(self, bar: abjad.Container):
        tuplet_index_tuple = (
            LeafMakerSequentialEventToQuantizedAbjadContainer._find_tuplet_indices(bar)
        )
        if tuplet_index_tuple:
            grouped_tuplet_index_list_list = (
                LeafMakerSequentialEventToQuantizedAbjadContainer._group_tuplet_indices(
                    tuplet_index_tuple
                )
            )
            for tuplet_index_list in reversed(grouped_tuplet_index_list_list):
                if len(tuplet_index_list) > 1:
                    LeafMakerSequentialEventToQuantizedAbjadContainer._concatenate_adjacent_tuplets_for_one_group(
                        bar, tuplet_index_list
                    )

    def _concatenate_adjacent_tuplets(self, voice: abjad.Voice) -> abjad.Voice:
        for bar in voice:
            self._concatenate_adjacent_tuplets_for_one_bar(bar)

    def _rewrite_meter(self, voice: abjad.Voice):
        time_signature_iter = iter(self._time_signature_tuple)
        last_time_signature = self._time_signature_tuple[-1]
        # rewrite by meter
        global_offset = abjad.Offset((0, 1))
        previous_time_signature = None
        for bar in voice:
            try:
                time_signature = next(time_signature_iter)
            except StopIteration:
                time_signature = last_time_signature
            if time_signature != previous_time_signature:
                abjad.attach(time_signature, abjad.get.leaf(bar, 0))
            meter = abjad.Meter(time_signature)
            abjad.Meter.rewrite_meter(
                bar[:], time_signature, maximum_dot_count=self._maximum_dot_count
            )
            if self._add_beams:
                global_offset = self._add_explicit_beams(bar, meter, global_offset)
            previous_time_signature = time_signature

        last_bar = bar
        difference = time_signature.duration - abjad.get.duration(last_bar)

        if difference:
            last_bar.extend(self._leaf_maker([None], [difference]))
            abjad.Meter.rewrite_meter(
                last_bar[:], time_signature, maximum_dot_count=self._maximum_dot_count
            )

    def _make_voice(
        self, sequential_event_to_convert: core_events.SequentialEvent
    ) -> abjad.Voice:
        # first build notes
        note_tuple = self._make_note_tuple(sequential_event_to_convert)

        # split notes by time signatures
        notes_split_by_time_signature_sequence = abjad.mutate.split(
            note_tuple,
            [time_signature.duration for time_signature in self._time_signature_tuple],
            cyclic=True,
        )
        bar_list = []
        for selection in notes_split_by_time_signature_sequence:
            try:
                bar = abjad.Container(selection, simultaneous=False)
            except Exception:
                bar = abjad.Container(
                    abjad.mutate.copy(selection), simultaneous=False
                )
            bar_list.append(bar)
        voice = abjad.Voice(bar_list)
        if self._do_rewrite_meter:
            self._rewrite_meter(voice)
        self._concatenate_adjacent_tuplets(voice)
        return voice

    def _get_data_for_leaf(
        self, index_tuple: tuple[int, ...], leaf: abjad.Leaf
    ) -> tuple[tuple[int, ...], bool, bool]:
        has_tie = abjad.get.indicator(leaf, abjad.Tie())
        is_rest = (
            isinstance(leaf, abjad.Rest)
            or isinstance(leaf, abjad.MultimeasureRest)
            or isinstance(leaf, abjad.Skip)
        )
        return index_tuple, has_tie, is_rest

    def _get_data_for_tuplet_or_leaf(
        self,
        index_tuple: tuple[int, ...],
        leaf_or_tuplet: typing.Union[abjad.Leaf, abjad.Tuplet],
    ) -> tuple[tuple[tuple[int, ...], bool], ...]:
        if isinstance(leaf_or_tuplet, abjad.Leaf):
            return (self._get_data_for_leaf(index_tuple, leaf_or_tuplet),)
        else:
            data_per_leaf_or_tuplet_list = []
            for nth_leaf_or_tuplet_of_tuplet, sub_leaf_or_tuplet in enumerate(
                leaf_or_tuplet
            ):
                data_per_leaf_or_tuplet_list.extend(
                    self._get_data_for_tuplet_or_leaf(
                        index_tuple + (nth_leaf_or_tuplet_of_tuplet,),
                        sub_leaf_or_tuplet,
                    )
                )
            return tuple(data_per_leaf_or_tuplet_list)

    def _make_related_abjad_leaves_per_simple_event(
        self, voice: abjad.Voice
    ) -> tuple[tuple[tuple[int, ...], ...], ...]:
        data_per_tuplet_or_leaf_list = []
        for nth_bar, bar in enumerate(voice):
            for nth_leaf_or_tuplet, leaf_or_tuplet in enumerate(bar):
                data_per_tuplet_or_leaf_list.extend(
                    self._get_data_for_tuplet_or_leaf(
                        (nth_bar, nth_leaf_or_tuplet), leaf_or_tuplet
                    )
                )

        related_abjad_leaves_per_simple_event = []
        related_abjad_leaves = []
        was_previous_note_rest = None
        has_previous_tie = None
        for index_tuple, has_tie, is_rest in data_per_tuplet_or_leaf_list:
            if has_previous_tie or all((was_previous_note_rest, is_rest)):
                related_abjad_leaves.append(index_tuple)
            else:
                if related_abjad_leaves:
                    related_abjad_leaves_per_simple_event.append(
                        tuple(related_abjad_leaves)
                    )
                related_abjad_leaves = [index_tuple]

            has_previous_tie = has_tie
            was_previous_note_rest = is_rest

        if related_abjad_leaves:
            related_abjad_leaves_per_simple_event.append(tuple(related_abjad_leaves))

        return tuple(related_abjad_leaves_per_simple_event)

    def convert(
        self, sequential_event_to_convert: core_events.SequentialEvent
    ) -> tuple[abjad.Container, tuple[tuple[tuple[int, ...], ...], ...],]:
        voice = self._make_voice(sequential_event_to_convert)
        related_abjad_leaves_per_simple_event = (
            self._make_related_abjad_leaves_per_simple_event(voice)
        )
        return voice, related_abjad_leaves_per_simple_event


class _DurationLineBasedQuantizedAbjadContainerMixin(object):
    """Mixin for duration-line based quantization.

    :param duration_line_minimum_length: The minimum length of a duration line.
    :type duration_line_minimum_length: int
    :param duration_line_thickness: The thickness of a duration line.
    :type duration_line_thickness: int

    This converter differs from its parent class through
    the usage of duration lines for indicating rhythm instead of using
    flags, beams, dots and note head colors.

    **Note**:

    Don't forget to add the 'Duration_line_engraver' to the resulting
    abjad Voice, otherwise Lilypond won't be able to render the desired output.

    **Example:**

    >>> import abjad
    >>> from mutwo import abjad_converters
    >>> from mutwo import core_events
    >>> converter = abjad_converters.SequentialEventToAbjadVoiceConverter(
    >>>     abjad_converters.LeafMakerSequentialEventToDurationLineBasedQuantizedAbjadContainer(
    >>>        )
    >>>    )
    >>> sequential_event_to_convert = core_events.SequentialEvent(
    >>>     [
    >>>         music_events.NoteLike("c", 0.125),
    >>>         music_events.NoteLike("d", 1),
    >>>         music_events.NoteLike([], 0.125),
    >>>         music_events.NoteLike("e", 0.16666),
    >>>         music_events.NoteLike("e", 0.08333333333333333)
    >>>     ]
    >>> )
    >>> converted_sequential_event = converter.convert(sequential_event_to_convert)
    >>> converted_sequential_event.consists_commands.append("Duration_line_engraver")
    """

    def __init__(
        self,
        *,
        duration_line_minimum_length: int = 6,
        duration_line_thickness: int = 3,
    ):
        self._duration_line_minimum_length = duration_line_minimum_length
        self._duration_line_thickness = duration_line_thickness

    @classmethod
    def _set_docs(cls, parent: type):
        doc_base = parent.__doc__.split("\n\n")
        doc_mixin = _DurationLineBasedQuantizedAbjadContainerMixin.__doc__.split("\n\n")

        cls.__doc__ = "\n\n".join(
            [doc_base[0], doc_base[1] + "\n" + doc_mixin[1]] + doc_mixin[2:]
        )

    def _prepare_first_element(self, first_element: abjad.Leaf):
        # set duration line properties
        abjad.attach(
            abjad.LilyPondLiteral(
                "\\override Staff.DurationLine.minimum-length = {}".format(
                    self._duration_line_minimum_length
                )
            ),
            first_element,
        )
        abjad.attach(
            abjad.LilyPondLiteral(
                "\\override Staff.DurationLine.thickness = {}".format(
                    self._duration_line_thickness
                )
            ),
            first_element,
        )

    def _adjust_quantisized_abjad_leaves(
        self,
        quanitisized_abjad_leaf_voice: abjad.Container,
        related_abjad_leaves_per_simple_event: tuple[tuple[tuple[int, ...], ...], ...],
    ):
        is_first = True

        for abjad_leaves_indices in related_abjad_leaves_per_simple_event:
            if abjad_leaves_indices:
                first_element = core_utilities.get_nested_item_from_index_sequence(
                    abjad_leaves_indices[0], quanitisized_abjad_leaf_voice
                )
                if is_first:
                    self._prepare_first_element(first_element)
                    is_first = False

                is_active = bool(abjad.get.pitches(first_element))
                if is_active:
                    if len(abjad_leaves_indices) > 1:
                        abjad.detach(abjad.Tie(), first_element)

                    abjad.attach(
                        abjad.LilyPondLiteral("\\-", site="after"), first_element
                    )

                    for indices in abjad_leaves_indices[1:]:
                        element = core_utilities.get_nested_item_from_index_sequence(
                            indices, quanitisized_abjad_leaf_voice
                        )
                        core_utilities.set_nested_item_from_index_sequence(
                            indices,
                            quanitisized_abjad_leaf_voice,
                            abjad.Skip(element.written_duration),
                        )


class NauertSequentialEventToDurationLineBasedQuantizedAbjadContainer(
    NauertSequentialEventToQuantizedAbjadContainer,
    _DurationLineBasedQuantizedAbjadContainerMixin,
):
    def __init__(
        self,
        *args,
        duration_line_minimum_length: int = 6,
        duration_line_thickness: int = 3,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        _DurationLineBasedQuantizedAbjadContainerMixin.__init__(
            self,
            duration_line_minimum_length=duration_line_minimum_length,
            duration_line_thickness=duration_line_thickness,
        )

    def convert(
        self, sequential_event_to_convert: core_events.SequentialEvent
    ) -> tuple[abjad.Container, tuple[tuple[tuple[int, ...], ...], ...],]:

        (
            quanitisized_abjad_leaf_voice,
            related_abjad_leaves_per_simple_event,
        ) = super().convert(sequential_event_to_convert)

        self._adjust_quantisized_abjad_leaves(
            quanitisized_abjad_leaf_voice, related_abjad_leaves_per_simple_event
        )

        return quanitisized_abjad_leaf_voice, related_abjad_leaves_per_simple_event


class LeafMakerSequentialEventToDurationLineBasedQuantizedAbjadContainer(
    LeafMakerSequentialEventToQuantizedAbjadContainer,
    _DurationLineBasedQuantizedAbjadContainerMixin,
):
    def __init__(
        self,
        *args,
        duration_line_minimum_length: int = 6,
        duration_line_thickness: int = 3,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        _DurationLineBasedQuantizedAbjadContainerMixin.__init__(
            self,
            duration_line_thickness=duration_line_thickness,
            duration_line_minimum_length=duration_line_minimum_length,
        )

    def convert(
        self, sequential_event_to_convert: core_events.SequentialEvent
    ) -> tuple[abjad.Container, tuple[tuple[tuple[int, ...], ...], ...],]:

        (
            quanitisized_abjad_leaf_voice,
            related_abjad_leaves_per_simple_event,
        ) = super().convert(sequential_event_to_convert)

        self._adjust_quantisized_abjad_leaves(
            quanitisized_abjad_leaf_voice, related_abjad_leaves_per_simple_event
        )

        # only assign first item to abjad leaves
        post_processed_releated_abjad_leaves_per_simple_event = []
        for related_abjad_leaves in related_abjad_leaves_per_simple_event:
            post_processed_releated_abjad_leaves_per_simple_event.append(
                (related_abjad_leaves[0],)
            )

        return (
            quanitisized_abjad_leaf_voice,
            post_processed_releated_abjad_leaves_per_simple_event,
        )


NauertSequentialEventToDurationLineBasedQuantizedAbjadContainer._set_docs(
    NauertSequentialEventToQuantizedAbjadContainer
)
LeafMakerSequentialEventToDurationLineBasedQuantizedAbjadContainer._set_docs(
    LeafMakerSequentialEventToQuantizedAbjadContainer
)
