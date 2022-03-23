"""Constants to be used in `mutwo.abjad_parameters"""

import abjad

INDICATORS_TO_DETACH_FROM_MAIN_LEAF_AT_GRACE_NOTES_TUPLE = (abjad.TimeSignature,)
"""This is used in :class:`mutwo.abjad_parameters.GraceNotes`.

Some indicators have to be detached from the main note and added to the first
grace note, otherwise the resulting notation will first print the grace notes
and afterwards the indicator (which is ugly and looks buggy)."""


# Cleanup
del abjad
