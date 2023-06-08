"""Constants for :mod:`mutwo.abjad_converters`.
"""

import abjad

INEFFECTIVE_INDICATOR_FOR_MULTIMEASURE_REST_TUPLE = (abjad.Fermata,)
"""Define indicators which don't work with multimeasure rests.

Some indicators aren't rendered in Lilypond when applied to multimeasure
rests. Therefore mutwo.abjad avoids creating multimeasure rests if a
to a rest any of the given indicator classes where attached.
"""

# Cleanup
del abjad
