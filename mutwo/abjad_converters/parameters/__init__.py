"""Module to convert mutwo parameters to abjad equivalents."""

from .lyrics import *
from .pitches import *
from .tempos import *
from .volumes import *

# Force flat structure
del lyrics, pitches, tempos, volumes


# Only import if mutwo.ext-ekmelily has been installed
try:
    from mutwo import ekmelily_converters
except ImportError:
    import logging

    logging.info(
        "Couldn't find 'ekmelily_converters.constants'. Please install "
        "package 'mutwo.ext-ekmelily' if you want to use "
        "'MutwoPitchToHEJIAbjadPitch'"
    )
    # Cleanup
    del logging
else:
    from .heji import *
    # Cleanup
    del heji
