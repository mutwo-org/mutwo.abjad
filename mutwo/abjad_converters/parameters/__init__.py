"""Module to convert mutwo parameters to abjad equivalents."""

from .lyrics import *
from .pitches import *
from .tempos import *
from .volumes import *

from . import lyrics, pitches, tempos, volumes

from mutwo import core_utilities

__all__ = core_utilities.get_all(lyrics, pitches, tempos, volumes)

# Force flat structure
del core_utilities, lyrics, pitches, tempos, volumes


# Only import if mutwo.ekmelily has been installed
try:
    from mutwo import ekmelily_converters
except ImportError:
    import logging

    logging.info(
        "Couldn't find 'ekmelily_converters.constants'. Please install "
        "package 'mutwo.ekmelily' if you want to use "
        "'MutwoPitchToHEJIAbjadPitch'"
    )
    # Cleanup
    del logging
else:
    from .heji import *

    from . import heji

    __all__ += heji.__all__

    # Cleanup
    del heji
