from __future__ import annotations
import abc
import dataclasses
import typing

import abjad

from mutwo import core_events
from mutwo import core_utilities
from mutwo import music_parameters


@dataclasses.dataclass()
class AbjadAttachment(abc.ABC):
    """Abstract base class for all Abjad attachments."""

    indicator: typing.Optional[
        music_parameters.abc.PlayingIndicator | music_parameters.abc.NotationIndicator
    ] = None
    is_simple_event_rest: typing.Optional[
        typing.Callable[[core_events.SimpleEvent], bool]
    ] = None
    mutwo_pitch_to_abjad_pitch: typing.Optional[
        typing.Callable[[music_parameters.abc.Pitch], abjad.Pitch]
    ] = None
    mutwo_pitch_to_abjad_pitch: typing.Optional[
        typing.Callable[[music_parameters.abc.Pitch], abjad.Pitch]
    ] = None
    mutwo_volume_to_abjad_attachment_dynamic: typing.Optional[
        typing.Callable[[music_parameters.abc.Volume], abjad.Dynamic]
    ] = None
    mutwo_lyric_to_abjad_string: typing.Optional[
        typing.Callable[[music_parameters.abc.Lyric], str]
    ] = None

    @classmethod
    def get_class_name(cls):
        return core_utilities.camel_case_to_snake_case(cls.__name__)

    @classmethod
    def from_indicator_collection(
        cls, indicator_collection: music_parameters.abc.IndicatorCollection, **kwargs
    ) -> typing.Optional[AbjadAttachment]:
        """Initialize :class:`AbjadAttachment` from :class:`~mutwo.parameters.abc.IndicatorCollection`.

        If no suitable :class:`~mutwo.parameters.abc.Indicator` could be found in the collection
        the method will simply return None.
        """

        class_name = cls.get_class_name()
        try:
            indicator = getattr(indicator_collection, class_name)
        except AttributeError:
            return None

        return cls(indicator, **kwargs)

    @abc.abstractmethod
    def process_leaf_tuple(
        self,
        leaf_tuple: tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional[AbjadAttachment],
    ) -> tuple[abjad.Leaf, ...]:
        ...

    @property
    def is_active(self) -> bool:
        return self.indicator.is_active


class ToggleAttachment(AbjadAttachment):
    """Abstract base class for Abjad attachments which behave like a toggle.

    In Western notation one can differentiate between elements which only get
    notated if they change (for instance dynamics, tempo) and elements which
    have to be notated again and again (for instance arpeggi or tremolo).
    Attachments that inherit from :class:`ToggleAttachment` represent elements
    which only get notated if their value changes.
    """

    @abc.abstractmethod
    def process_leaf(
        self, leaf: abjad.Leaf, previous_attachment: typing.Optional[AbjadAttachment]
    ) -> abjad.Leaf | typing.Sequence[abjad.Leaf]:
        ...

    def process_leaf_tuple(
        self,
        leaf_tuple: tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional[AbjadAttachment],
    ) -> tuple[abjad.Leaf, ...]:
        if previous_attachment != self:
            return (
                self.process_leaf(leaf_tuple[0], previous_attachment),
            ) + leaf_tuple[1:]
        else:
            return leaf_tuple


class BangAttachment(AbjadAttachment):
    """Abstract base class for Abjad attachments which behave like a bang.

    In Western notation one can differentiate between elements which only get
    notated if they change (for instance dynamics, tempo) and elements which
    have to be notated again and again to be effective (for instance arpeggi or
    tremolo). Attachments that inherit from :class:`BangAttachment` represent
    elements which have to be notated again and again to be effective.
    """

    @abc.abstractmethod
    def process_first_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        ...

    @abc.abstractmethod
    def process_last_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        ...

    @abc.abstractmethod
    def process_central_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        ...

    def process_leaf_tuple(
        self,
        leaf_tuple: tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional[AbjadAttachment],
    ) -> tuple[abjad.Leaf, ...]:
        new_leaf_list = []

        if (leaf_count := len(leaf_tuple)) > 0:
            new_leaf_list.append(self.process_first_leaf(leaf_tuple[0]))
        if leaf_count > 2:
            for leaf in leaf_tuple[1:-1]:
                new_leaf_list.append(self.process_central_leaf(leaf))
        if leaf_count > 1:
            new_leaf_list.append(self.process_last_leaf(leaf_tuple[-1]))

        return tuple(new_leaf_list)


class BangEachAttachment(BangAttachment):
    @abc.abstractmethod
    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> abjad.Leaf | typing.Sequence[abjad.Leaf]:
        ...

    def process_first_leaf(
        self, leaf: abjad.Leaf
    ) -> abjad.Leaf | typing.Sequence[abjad.Leaf]:
        return self.process_leaf(leaf)

    def process_last_leaf(
        self, leaf: abjad.Leaf
    ) -> abjad.Leaf | typing.Sequence[abjad.Leaf]:
        return self.process_leaf(leaf)

    def process_central_leaf(
        self, leaf: abjad.Leaf
    ) -> abjad.Leaf | typing.Sequence[abjad.Leaf]:
        return self.process_leaf(leaf)


class BangFirstAttachment(BangAttachment):
    @abc.abstractmethod
    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> abjad.Leaf | typing.Sequence[abjad.Leaf]:
        ...

    def process_first_leaf(
        self, leaf: abjad.Leaf
    ) -> abjad.Leaf | typing.Sequence[abjad.Leaf]:
        return self.process_leaf(leaf)

    def process_last_leaf(
        self, leaf: abjad.Leaf
    ) -> abjad.Leaf | typing.Sequence[abjad.Leaf]:
        return leaf

    def process_central_leaf(
        self, leaf: abjad.Leaf
    ) -> abjad.Leaf | typing.Sequence[abjad.Leaf]:
        return leaf


class BangLastAttachment(BangAttachment):
    @abc.abstractmethod
    def process_leaf(
        self, leaf: abjad.Leaf
    ) -> abjad.Leaf | typing.Sequence[abjad.Leaf]:
        ...

    def process_first_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        return leaf

    def process_last_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        return self.process_leaf(leaf)

    def process_central_leaf(self, leaf: abjad.Leaf) -> abjad.Leaf:
        return leaf

    def process_leaf_tuple(
        self,
        leaf_tuple: tuple[abjad.Leaf, ...],
        previous_attachment: typing.Optional[AbjadAttachment],
    ) -> tuple[abjad.Leaf, ...]:
        if len(leaf_tuple) > 0:
            return leaf_tuple[:-1] + (self.process_last_leaf(leaf_tuple[-1]),)
        else:
            return leaf_tuple
