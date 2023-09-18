__all__ = ("NoTimeSignatureError",)


class NoTimeSignatureError(Exception):
    def __init__(self):
        super().__init__(
            "Found empty sequence for argument "
            "'default_time_signature_sequence_count'. "
            "Specify at least one time signature!"
        )
