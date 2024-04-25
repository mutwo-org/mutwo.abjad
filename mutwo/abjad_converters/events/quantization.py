"""Module to quantize free :class:`Consecution` to notation based abjad :class:`Container`"""

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

from mutwo import abjad_utilities
from mutwo import core_converters
from mutwo import core_events
from mutwo import core_parameters
from mutwo import core_utilities

__all__ = (
    "ConsecutionToQuantizedAbjadContainer",
    "NauertConsecutionToQuantizedAbjadContainer",
    "NauertConsecutionToDurationLineBasedQuantizedAbjadContainer",
    "LeafMakerConsecutionToQuantizedAbjadContainer",
    "LeafMakerConsecutionToDurationLineBasedQuantizedAbjadContainer",
)


IsChrononRestTuple: typing.TypeAlias = tuple[bool, ...]
QuantizationData: typing.TypeAlias = tuple[
    abjad.Container, tuple[tuple[tuple[int, ...], ...], ...], IsChrononRestTuple
]


# XXX: In the future `default_tempo_envelope` should be set to `None` and
# `mutwo` should, by default, use `event_to_tempo_envelope`. Then
# `default_tempo_envelope` should be removed completely.
class ConsecutionToQuantizedAbjadContainer(core_converters.abc.Converter):
    """Quantize :class:`~mutwo.core_events.Consecution` objects.

    :param default_time_signature_sequence: Set time signatures to divide the quantized abjad data
        in desired bar sizes. If the converted :class:`~mutwo.core_events.Consecution`
        is longer than the sum of all passed time signatures, the last time signature
        will be repeated for the remaining bars.
    :type default_time_signature_sequence: typing.Sequence[abjad.TimeSignature]
    :param event_to_time_signature_tuple: Function which extracts a
        `tuple[abjad.TimeSignature, ...]` from a :class:`mutwo.core_events.abc.Event`.
        If set to `None` `mutwo` falls back to `default_time_signature_sequence`.
        Default to `None`.
    :param is_chronon_rest: Function to detect if the
        the inspected :class:`mutwo.core_events.Chronon` is a Rest. By
        default Mutwo simply checks if 'pitch_list' contain any objects. If not,
        the Event will be interpreted as a rest.
    :type is_chronon_rest: typing.Callable[[core_events.Chronon], bool], optional
    """

    def __init__(
        self,
        default_time_signature_sequence: typing.Sequence[abjad.TimeSignature] = (
            abjad.TimeSignature((4, 4)),
        ),
        event_to_time_signature_tuple: typing.Optional[
            typing.Callable[
                [core_events.abc.Event],
                typing.Optional[tuple[abjad.TimeSignature, ...]],
            ]
        ] = None,
        is_chronon_rest: typing.Optional[
            typing.Callable[[core_events.Chronon], bool]
        ] = None,
    ):
        default_time_signature_sequence_count = len(default_time_signature_sequence)
        if default_time_signature_sequence_count == 0:
            raise abjad_utilities.NoTimeSignatureError()

        if is_chronon_rest is None:

            def is_chronon_rest(chronon: core_events.Chronon) -> bool:
                pitch_list = core_utilities.call_function_except_attribute_error(
                    lambda e: e.pitch_list, chronon, []
                )
                return not bool(pitch_list)

        default_time_signature_tuple = tuple(default_time_signature_sequence)
        self._default_time_signature_tuple = default_time_signature_tuple

        self._event_to_time_signature_tuple = event_to_time_signature_tuple

        self._is_chronon_rest = is_chronon_rest

    def _get_time_signature_tuple(
        self, event: core_events.abc.Event
    ) -> tuple[abjad.TimeSignature, ...]:
        if self._event_to_time_signature_tuple:
            if time_signature_tuple := self._event_to_time_signature_tuple(event):
                return time_signature_tuple
        return self._default_time_signature_tuple

    def _tie_rests(self, consecution_to_convert: core_events.Consecution):
        # Tie rests before further processing the event
        #
        # We need to do this, because otherwise pitches/volumes/indicators
        # don't get attached to the right leaves, since
        # 'related_abjad_leaf_index_tuple_tuple_per_chronon' would point
        # to rests where notes are expected. This is because the quantizer
        # auto-splits and auto-combines rests in the following cases:
        #
        #   - if they are too long and span across two bars
        #   - if they are pointless (e.g. first beat of 4/4 bar 1/16 and a 3/16
        #     rest would be combined to a 1/4 rest) the quantizer
        #     automatically combines them (in 'rewrite_meter').
        #
        # These auto-split and auto-merge rest cases are considered as
        # features (the main functionality of this quantizer:
        # care about all annoying notational details we don't want to
        # care about) and not as bugs. But they lead to the limitation, that
        # in this mode we can't apply indicators to two adjacent rests.
        #
        # Maybe there would be a way to support the auto-merge and
        # auto-split, while still persisting indicators on a rest sequence.
        # For this, the quantizer would need to only tie rests, that
        # don't contain any playing or notation indicators. Furthermore
        # it would be disallowed to auto-merge rests in further proceedings
        # (as rewrite_meter or concatenate_adjacent_tuplets) that have
        # indicators applied to them. For this we would need to pin tags to
        # events according to their status.
        return consecution_to_convert.copy().tie_by(
            lambda event0, event1: self._is_chronon_rest(event0)
            and self._is_chronon_rest(event1),
            event_type_to_examine=core_events.Chronon,
        )

    def _apply_is_rest(self, consecution_to_convert: core_events.Consecution):
        # Apply 'is_rest' attribute to each event in the 'Consecution'
        # (this is needed for further proceedings)
        is_chronon_rest_tuple = tuple(
            self._is_chronon_rest(chronon) for chronon in consecution_to_convert
        )
        is_chronon_rest_iterator = iter(is_chronon_rest_tuple)
        return (
            consecution_to_convert.copy().set_parameter(  # type: ignore
                "is_rest",
                lambda _: next(is_chronon_rest_iterator),
                set_unassigned_parameter=True,
            ),
            is_chronon_rest_tuple,
        )

    # ###################################################################### #
    #               public methods for interaction with the user             #
    # ###################################################################### #

    @abc.abstractmethod
    def convert(
        self, consecution_to_convert: core_events.Consecution
    ) -> QuantizationData:
        ...


class NauertConsecutionToQuantizedAbjadContainer(ConsecutionToQuantizedAbjadContainer):
    """Quantize :class:`~mutwo.core_events.Consecution` objects via :mod:`abjadext.nauert`.

    :param default_time_signature_sequence: Set time signatures to divide the quantized abjad data
        in desired bar sizes. If the converted :class:`~mutwo.core_events.Consecution`
        is longer than the sum of all passed time signatures, the last time signature
        will be repeated for the remaining bars.
    :type default_time_signature_sequence: typing.Sequence[abjad.TimeSignature]
    :param duration_unit: This defines the `duration_unit` of the passed
        :class:`~mutwo.core_events.Consecution` (how the
        :attr:`~mutwo.core_events.abc.Event.duration` attribute will be
        interpreted). Can either be 'beats' (default) or 'miliseconds'.
        WARNING: 'miliseconds' isn't working properly yet!
    :param attack_point_optimizer: Optionally the user can pass a
        :class:`nauert.AttackPointOptimizer` object. Attack point optimizer help to
        split events and tie them for better looking notation. The default attack point
        optimizer is :class:`nauert.MeasurewiseAttackPointOptimizer` which splits events
        to better represent metrical structures within bars. If no optimizer is desired
        this argument can be set to ``None``.

    Unlike :class:`LeafMakerConsecutionToQuantizedAbjadContainer` this converter
    supports nested tuplets and ties across tuplets. But this converter is much slower
    than the :class:`LeafMakerConsecutionToQuantizedAbjadContainer`. Because the
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
        default_time_signature_sequence: typing.Sequence[abjad.TimeSignature] = (
            abjad.TimeSignature((4, 4)),
        ),
        duration_unit: str = "beats",  # for future: typing.Literal["beats", "miliseconds"]
        attack_point_optimizer: typing.Optional[
            nauert.AttackPointOptimizer
        ] = nauert.MeasurewiseAttackPointOptimizer(),
        search_tree: typing.Optional[nauert.SearchTree] = None,
        **kwargs,
    ):
        if duration_unit == "miliseconds":
            # warning for not well implemented miliseconds conversion

            warnings.warn(
                "The current implementation can't apply tempo changes for duration unit"
                " 'miliseconds' yet! Furthermore to quantize via duration_unit"
                " 'miliseconds' isn't well tested yet and may return unexpected"
                " results."
            )

        default_time_signature_tuple = tuple(default_time_signature_sequence)
        # nauert will raise an error if there is only one time signature
        if len(default_time_signature_tuple) == 1:
            default_time_signature_tuple += default_time_signature_tuple

        super().__init__(default_time_signature_tuple, **kwargs)

        self._duration_unit = duration_unit
        self._attack_point_optimizer = attack_point_optimizer
        self._search_tree = search_tree

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
        related_abjad_leaves_per_chronon: list[list[tuple[int, ...]]],
        q_event_sequence: nauert.QEventSequence,
        has_tie: bool,
        index_of_previous_q_event: int,
    ) -> tuple[bool, int]:
        q_event = NauertConsecutionToQuantizedAbjadContainer._get_respective_q_event_from_abjad_leaf(
            abjad_leaf
        )

        if q_event and type(q_event) != nauert.TerminalQEvent:
            nth_q_event = q_event_sequence.sequence.index(q_event)
            related_abjad_leaves_per_chronon[nth_q_event].append(tuple(indices))
            index_of_previous_q_event = nth_q_event
        elif has_tie:
            related_abjad_leaves_per_chronon[index_of_previous_q_event].append(
                tuple(indices)
            )
        # skip leaves without any links
        # else:
        #     related_abjad_leaves_per_chronon.append([tuple(indices)])

        has_tie = abjad.get.has_indicator(abjad_leaf, abjad.Tie)

        return has_tie, index_of_previous_q_event

    @staticmethod
    def _process_tuplet(
        indices: list[int],
        tuplet: abjad.Tuplet,
        related_abjad_leaves_per_chronon: list[list[tuple[int, ...]]],
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
            ) = NauertConsecutionToQuantizedAbjadContainer._process_abjad_leaf_or_tuplet(
                indices + [nth_abjad_leaf_or_tuplet],
                abjad_leaf_or_tuplet,
                related_abjad_leaves_per_chronon,
                q_event_sequence,
                has_tie,
                index_of_previous_q_event,
            )

        return has_tie, index_of_previous_q_event

    @staticmethod
    def _process_abjad_leaf_or_tuplet(
        index_list: list[int],
        abjad_leaf_or_tuplet: typing.Union[abjad.Tuplet, abjad.Leaf],
        related_abjad_leaves_per_chronon: list[list[tuple[int, ...]]],
        q_event_sequence: nauert.QEventSequence,
        has_tie: bool,
        index_of_previous_q_event: int,
    ) -> tuple[bool, int]:
        if isinstance(abjad_leaf_or_tuplet, abjad.Tuplet):
            return NauertConsecutionToQuantizedAbjadContainer._process_tuplet(
                index_list,
                abjad_leaf_or_tuplet,
                related_abjad_leaves_per_chronon,
                q_event_sequence,
                has_tie,
                index_of_previous_q_event,
            )

        else:
            return NauertConsecutionToQuantizedAbjadContainer._process_abjad_leaf(
                index_list,
                abjad_leaf_or_tuplet,
                related_abjad_leaves_per_chronon,
                q_event_sequence,
                has_tie,
                index_of_previous_q_event,
            )

    @staticmethod
    def _make_related_abjad_leaves_per_chronon(
        consecution: core_events.Consecution,
        q_event_sequence: nauert.QEventSequence,
        quanitisized_abjad_leaf_voice: abjad.Voice,
    ) -> tuple[tuple[tuple[int, ...], ...], ...,]:
        has_tie = False
        index_of_previous_q_event: int = 0
        related_abjad_leaves_per_chronon: list[list[tuple[int, ...]]] = [
            [] for _ in consecution
        ]
        for nth_bar, bar in enumerate(quanitisized_abjad_leaf_voice):
            for nth_abjad_leaf_or_tuplet, abjad_leaf_or_tuplet in enumerate(bar):
                (
                    has_tie,
                    index_of_previous_q_event,
                ) = NauertConsecutionToQuantizedAbjadContainer._process_abjad_leaf_or_tuplet(
                    [nth_bar, nth_abjad_leaf_or_tuplet],
                    abjad_leaf_or_tuplet,
                    related_abjad_leaves_per_chronon,
                    q_event_sequence,
                    has_tie,
                    index_of_previous_q_event,
                )

        return tuple(
            tuple(tuple(item) for item in pair)
            for pair in related_abjad_leaves_per_chronon
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

    def _get_q_schema(self, event: core_events.abc.Event) -> nauert.MeasurewiseQSchema:
        return NauertConsecutionToQuantizedAbjadContainer._make_q_schema(
            self._get_time_signature_tuple(event), self._search_tree
        )

    def _consecution_to_q_event_sequence(
        self, consecution: core_events.Consecution
    ) -> nauert.QEventSequence:
        duration_list = list(
            map(to_abjad_compatible_duration, consecution.get_parameter("duration"))
        )

        for nth_chronon, chronon in enumerate(consecution):
            if chronon.is_rest:
                duration_list[nth_chronon] = (
                    0 - duration_list[nth_chronon]
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
        self,
        q_event_sequence: nauert.QEventSequence,
        q_schema: nauert.MeasurewiseQSchema,
    ) -> abjad.Voice:
        quantizer = nauert.Quantizer()
        return quantizer(
            q_event_sequence,
            q_schema=q_schema,
            attach_tempos=True if self._duration_unit == "miliseconds" else False,
            attack_point_optimizer=self._attack_point_optimizer,
        )

    # ###################################################################### #
    #               public methods for interaction with the user             #
    # ###################################################################### #

    def convert(
        self, consecution_to_convert: core_events.Consecution
    ) -> QuantizationData:
        consecution_to_convert, is_chronon_rest_tuple = self._apply_is_rest(
            self._tie_rests(consecution_to_convert)
        )
        q_event_sequence = self._consecution_to_q_event_sequence(consecution_to_convert)
        q_schema = self._get_q_schema(consecution_to_convert)
        quanitisized_abjad_leaf_voice = (
            self._q_event_sequence_to_quanitisized_abjad_leaf_voice(
                q_event_sequence, q_schema
            )
        )

        related_abjad_leaves_per_chronon = NauertConsecutionToQuantizedAbjadContainer._make_related_abjad_leaves_per_chronon(
            consecution_to_convert, q_event_sequence, quanitisized_abjad_leaf_voice
        )
        return (
            quanitisized_abjad_leaf_voice,
            related_abjad_leaves_per_chronon,
            is_chronon_rest_tuple,
        )


class LeafMakerConsecutionToQuantizedAbjadContainer(
    ConsecutionToQuantizedAbjadContainer
):
    """Quantize :class:`~mutwo.core_events.Consecution` object via :mod:`abjad.LeafMaker`.

    :param default_time_signature_sequence: Set time signatures to divide the quantized abjad data
        in desired bar sizes. If the converted
        :class:`~mutwo.core_events.Consecution` is longer than the sum of
        all passed time signatures, the last time signature
        will be repeated for the remaining bars.
    :type default_time_signature_sequence: typing.Sequence[abjad.TimeSignature]
    :param concatenate_adjacent_tuplets: Set to `True` if quantizer should concatenate
        adjacent tuplets via :func:`mutwo.abjad_utilities.concatenate_adjacent_tuplets`.
        Because this function can make processing slower (and may lead to not-yet-fixed
        bugs) it can be deactivated if not used. Default to `True`.
    :type concatenate_adjacent_tuplets: bool
    :param reduce_multiplier: Set to `True` if quantizer should call
        :func:`mutwo.abjad_utilities.reduce_multiplier` after consecution
        has been quantized. Can be useful if working with tuplets. If no tuplets
        are used it can be deactivated for faster conversion. Default to ``True``.
    :type reduce_multiplier: bool

    This method is significantly faster than the
    :class:`NauertConsecutionToQuantizedAbjadContainer`. But it also
    has several known limitations:

        1. :class:`LeafMakerConsecutionToQuantizedAbjadContainer` doesn't
           support nested tuplets.
        2. :class:`LeafMakerConsecutionToQuantizedAbjadContainer` doesn't
           support ties across tuplets with different prolation (or across tuplets
           and not-tuplet notation). If ties are desired the user has to build them
           manually before passing the :class:`~mutwo.core_events.Consecution`
           to the converter.
    """

    _maximum_dot_count = 1

    def __init__(
        self,
        *args,
        do_rewrite_meter: bool = True,
        add_beams: bool = True,
        concatenate_adjacent_tuplets: bool = True,
        reduce_multiplier: bool = True,
        **kwargs,
    ):
        self._leaf_maker = abjad.LeafMaker(
            forbidden_note_duration=abjad.Duration(8, 1),
            forbidden_rest_duration=abjad.Duration(8, 1),
        )
        super().__init__(*args, **kwargs)
        self._concatenate_adjacent_tuplets = concatenate_adjacent_tuplets
        self._do_rewrite_meter = do_rewrite_meter
        self._add_beams = add_beams
        self._reduce_multiplier = reduce_multiplier

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
            LeafMakerConsecutionToQuantizedAbjadContainer._find_offset_inventory(meter)
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

    # ###################################################################### #
    #                       private methods                                  #
    # ###################################################################### #

    def _make_note_tuple(
        self, consecution_to_convert: core_events.Consecution
    ) -> tuple[abjad.Leaf, ...]:
        pitch_list = [
            None if event.is_rest else "c" for event in consecution_to_convert
        ]
        # It has to be a list! Otherwise abjad raises an exception.
        duration_list = list(
            map(
                lambda duration: abjad.Duration(to_abjad_compatible_duration(duration)),
                consecution_to_convert.get_parameter("duration"),
            )
        )
        note_tuple = tuple(self._leaf_maker(pitch_list, duration_list))
        return note_tuple

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
        self, consecution_to_convert: core_events.Consecution
    ) -> abjad.Voice:
        # first build notes
        note_tuple = self._make_note_tuple(consecution_to_convert)

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
                bar = abjad.Container(abjad.mutate.copy(selection), simultaneous=False)
            bar_list.append(bar)
        voice = abjad.Voice(bar_list)
        if self._do_rewrite_meter:
            self._rewrite_meter(voice)
        if self._concatenate_adjacent_tuplets:
            abjad_utilities.concatenate_adjacent_tuplets(voice)
        if self._reduce_multiplier:
            abjad_utilities.reduce_multiplier(voice)
        return voice

    def _get_data_for_leaf(
        self, index_tuple: tuple[int, ...], leaf: abjad.Leaf
    ) -> tuple[tuple[int, ...], bool, bool]:
        has_tie = abjad.get.indicator(leaf, abjad.Tie())
        is_rest = isinstance(leaf, (abjad.Rest, abjad.MultimeasureRest, abjad.Skip))
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

    def _make_related_abjad_leaves_per_chronon(
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

        related_abjad_leaves_per_chronon = []
        related_abjad_leaves = []
        was_previous_note_rest = None
        has_previous_tie = None
        for index_tuple, has_tie, is_rest in data_per_tuplet_or_leaf_list:
            if has_previous_tie or all((was_previous_note_rest, is_rest)):
                related_abjad_leaves.append(index_tuple)
            else:
                if related_abjad_leaves:
                    related_abjad_leaves_per_chronon.append(tuple(related_abjad_leaves))
                related_abjad_leaves = [index_tuple]

            has_previous_tie = has_tie
            was_previous_note_rest = is_rest

        if related_abjad_leaves:
            related_abjad_leaves_per_chronon.append(tuple(related_abjad_leaves))

        return tuple(related_abjad_leaves_per_chronon)

    def convert(
        self, consecution_to_convert: core_events.Consecution
    ) -> QuantizationData:
        consecution_to_convert, is_chronon_rest_tuple = self._apply_is_rest(
            self._tie_rests(consecution_to_convert)
        )
        self._time_signature_tuple = self._get_time_signature_tuple(
            consecution_to_convert
        )
        voice = self._make_voice(consecution_to_convert)
        related_abjad_leaves_per_chronon = self._make_related_abjad_leaves_per_chronon(
            voice
        )
        return voice, related_abjad_leaves_per_chronon, is_chronon_rest_tuple


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
    >>> from mutwo import core_events, music_events
    >>> converter = abjad_converters.ConsecutionToAbjadVoice(
    ...     abjad_converters.LeafMakerConsecutionToDurationLineBasedQuantizedAbjadContainer(
    ...        )
    ...    )
    >>> seq = core_events.Consecution(
    ...     [
    ...         music_events.NoteLike("c", 0.25),
    ...         music_events.NoteLike("d", 1),
    ...         music_events.NoteLike([], 0.25),
    ...         music_events.NoteLike("e", 1),
    ...         music_events.NoteLike("e", 1)
    ...     ]
    ... )
    >>> voice = converter.convert(seq)
    >>> voice.consists_commands.append("Duration_line_engraver")
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
        related_abjad_leaves_per_chronon: tuple[tuple[tuple[int, ...], ...], ...],
    ):
        is_first = True

        for abjad_leaves_indices in related_abjad_leaves_per_chronon:
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


class NauertConsecutionToDurationLineBasedQuantizedAbjadContainer(
    NauertConsecutionToQuantizedAbjadContainer,
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
        self, consecution_to_convert: core_events.Consecution
    ) -> QuantizationData:
        (
            quanitisized_abjad_leaf_voice,
            related_abjad_leaves_per_chronon,
            is_chronon_rest_tuple,
        ) = super().convert(consecution_to_convert)

        self._adjust_quantisized_abjad_leaves(
            quanitisized_abjad_leaf_voice, related_abjad_leaves_per_chronon
        )

        return (
            quanitisized_abjad_leaf_voice,
            related_abjad_leaves_per_chronon,
            is_chronon_rest_tuple,
        )


class LeafMakerConsecutionToDurationLineBasedQuantizedAbjadContainer(
    LeafMakerConsecutionToQuantizedAbjadContainer,
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
        self, consecution_to_convert: core_events.Consecution
    ) -> QuantizationData:
        (
            quanitisized_abjad_leaf_voice,
            related_abjad_leaves_per_chronon,
            is_chronon_rest_tuple,
        ) = super().convert(consecution_to_convert)

        self._adjust_quantisized_abjad_leaves(
            quanitisized_abjad_leaf_voice, related_abjad_leaves_per_chronon
        )

        # only assign first item to abjad leaves
        post_processed_releated_abjad_leaves_per_chronon = []
        for related_abjad_leaves in related_abjad_leaves_per_chronon:
            post_processed_releated_abjad_leaves_per_chronon.append(
                (related_abjad_leaves[0],)
            )

        return (
            quanitisized_abjad_leaf_voice,
            post_processed_releated_abjad_leaves_per_chronon,
            is_chronon_rest_tuple,
        )


NauertConsecutionToDurationLineBasedQuantizedAbjadContainer._set_docs(
    NauertConsecutionToQuantizedAbjadContainer
)
LeafMakerConsecutionToDurationLineBasedQuantizedAbjadContainer._set_docs(
    LeafMakerConsecutionToQuantizedAbjadContainer
)


def to_abjad_compatible_duration(duration: core_parameters.abc.Duration):
    return getattr(duration, "ratio", None) or duration.beat_count
