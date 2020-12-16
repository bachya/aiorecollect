"""Define library exception types."""


class RecollectError(Exception):
    """Define a base ReCollect Waste exception."""

    pass


class RequestError(RecollectError):
    """Define a exception related to HTTP request errors."""

    pass


class DataError(RecollectError):
    """Define an exception related to invalid/missing data."""

    pass
