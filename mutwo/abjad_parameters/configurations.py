"""Configure `mutwo.abjad_parameters"""

CUSTOM_STRING_CONTACT_POINT_DICT = {"col legno tratto": "c.l.t."}
"""Extends the predefined string contact points from :class:`abjad.StringContactPoint`.

The ``dict`` has the form `{string_contact_point: abbreviation}`. It is used
in the class :class:`~mutwo.abjad_parameters.StringContactPoint`.
You can override or update the default value of the variable to insert your own
custom string contact points:

    >>> from mutwo import abjad_parameters
    >>> abjad_parameters.configurations.CUSTOM_STRING_CONTACT_POINT_DICT.update({"ebow": "eb"})
"""
