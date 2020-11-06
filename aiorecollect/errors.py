"""Define library exception types."""


class RecollectError(Exception):
    """Define a base Recollect Waste exception."""

    pass


class RequestError(RecollectError):
    """Define a exception related to HTTP request errors."""

    pass
