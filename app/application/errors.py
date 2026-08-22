"""Application error types.

The original code threw the framework exceptions below; Python equivalents
are kept as separate classes so the bot layer can catch them explicitly.

===============  ==========================
C# exception     Python error
===============  ==========================
KeyNotFoundException  ``KeyNotFoundError``
UnauthorizedAccessException  ``UnauthorizedError``
InvalidOperationException   ``InvalidOperationError``
OverflowException           builtin ``OverflowError`` (used for the
                            subscription limit, matching the C#)
===============  ==========================
"""

from __future__ import annotations


class KeyNotFoundError(Exception):
    """C# ``KeyNotFoundException``."""


class UnauthorizedError(Exception):
    """C# ``UnauthorizedAccessException``."""


class InvalidOperationError(Exception):
    """C# ``InvalidOperationException``."""


class MaxRetriesError(Exception):
    """C# ``Exception("max_retries")`` thrown by ``GetSeatsAsync``."""


class HttpRequestError(Exception):
    """HTTP-level failure (transport/status); wraps ``httpx`` errors.

    Raised by the infrastructure client so the application/notifier layers
    do not depend on httpx.
    """
