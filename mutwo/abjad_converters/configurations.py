"""Configure :mod:`mutwo.abjad_converters`.
"""

import inspect

from mutwo import abjad_parameters

DEFAULT_ABJAD_ATTACHMENT_CLASS_TUPLE = tuple(
    cls
    for _, cls in inspect.getmembers(abjad_parameters, inspect.isclass)
    if not inspect.isabstract(cls)
    and abjad_parameters.abc.AbjadAttachment in inspect.getmro(cls)
)
"""Default value for argument `abjad_attachment_classes` in
:class:`~mutwo.abjad_converters.ConsecutionToAbjadVoiceConverter`."""

# Cleanup
del abjad_parameters, inspect
