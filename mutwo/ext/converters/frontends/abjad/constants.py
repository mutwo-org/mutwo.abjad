"""Constants to be used for and with :mod:`mutwo.ext.converters.frontends.abjad`.
"""

import inspect

from mutwo.ext.converters.frontends.abjad import attachments

DEFAULT_ABJAD_ATTACHMENT_CLASS_TUPLE = tuple(
    cls
    for _, cls in inspect.getmembers(attachments, inspect.isclass)
    if not inspect.isabstract(cls)
)
"""Default value for argument `abjad_attachment_classes` in
:class:`~mutwo.ext.converters.frontends.SequentialEventToAbjadVoiceConverter`."""
