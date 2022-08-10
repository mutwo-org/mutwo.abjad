"""Build Lilypond scores via `Abjad <https://github.com/Abjad/abjad>`_ from Mutwo data.

The following converter classes help to quantize and translate Mutwo data to
Western notation. Due to the complex nature of this task, Mutwo tries to offer as
many optional arguments as possible through which the user can affect the conversion
routines. The most important class and best starting point for organising a conversion
setting is :class:`SequentialEventToAbjadVoiceConverter`.
If one wants to build complete scores from within mutwo, the module offers the
:class:`NestedComplexEventToAbjadContainerConverter`.

**Known bugs and limitations:**

1. Indicators attached to rests which follow another rest won't be translated to
   `abjad`. This behaviour happens because the
   :class:`~mutwo.abjad_converters.SequentialEventToAbjadVoiceConverter`
   ties rests before converting the data to `abjad` objects.

2. Quantization can be slow and not precise. Try both quantization classes.
   Change the parameters. Use different settings and classes for different
   parts of your music.
"""

# Apply monkey patch
from mutwo_third_party import abjad

from . import configurations

from .process_container_routines import *

from .parameters import *
from .events import *

from . import events, parameters, process_container_routines

from mutwo import core_utilities

__all__ = core_utilities.get_all(events, parameters, process_container_routines)

# Force flat structure
del core_utilities, events, parameters, process_container_routines

# Remove unused third party import
# XXX: We have to import it because otherwise the
# monkey patches won't be applied.
del abjad
