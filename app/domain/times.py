"""Time helpers reproducing the legacy ``UTC-3`` storage quirk.

The original ``TrainVO`` stores departure/arrival times in DB (`jsonb`) as
``HH:mm:ss`` strings computed as *local (Minsk, UTC+3) time minus 3 hours*,
and reads them back by adding 3 hours. These helpers replicate that exact
wall-clock arithmetic, including wrap-around across midnight.
"""

from __future__ import annotations

import datetime

UTC_OFFSET = datetime.timedelta(hours=3)
_EPOCH = datetime.datetime(1970, 1, 1, tzinfo=datetime.UTC)


def unix_seconds_to_local_time(unix: int) -> datetime.time:
    """C# ``UnixTimeToTimeOnly``: UTC epoch seconds + 3 hours -> wall clock."""
    moment = _EPOCH + datetime.timedelta(seconds=unix) + UTC_OFFSET
    return moment.time()


def local_time_to_storage(value: datetime.time, hours: int = 3) -> str:
    """C# ``Write``: ``HH:mm:ss`` of ``value`` shifted *back* by ``hours``."""
    total = (value.hour * 3600 + value.minute * 60 + value.second - hours * 3600) % 86400
    hh, rem = divmod(total, 3600)
    mm, ss = divmod(rem, 60)
    return f"{hh:02d}:{mm:02d}:{ss:02d}"


def storage_string_to_local_time(raw: str, hours: int = 3) -> datetime.time:
    """C# ``Read``: ``HH:mm:ss`` string shifted *forward* by ``hours``."""
    parts = raw.split(":")
    if len(parts) != 3:
        raise ValueError(f"Invalid time format: {raw!r}")
    total = (int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2]) + hours * 3600) % 86400
    hh, rem = divmod(total, 3600)
    mm, ss = divmod(rem, 60)
    return datetime.time(hh, mm, ss)
