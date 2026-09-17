"""Date/time parsing helpers used by the handlers.

Mirrors the C# ``DateOnly.TryParseExact(..., "dd.MM.yyyy")``,
``DateTime.AddMonths`` and ``TimeSpan.TryParse`` behaviours the original
handlers relied on.
"""

from __future__ import annotations

import calendar
import datetime
import re

_DATE_RE = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")


def add_months(date: datetime.date, months: int) -> datetime.date:
    """``DateTime.AddMonths`` — clamps day to the target month's length."""
    month_index = date.month - 1 + months
    year = date.year + month_index // 12
    month = month_index % 12 + 1
    day = min(date.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def parse_date_exact(text: str) -> datetime.date | None:
    """``DateOnly.TryParseExact(text, "dd.MM.yyyy")``."""
    if not _DATE_RE.match(text):
        return None
    day, month, year = (int(part) for part in text.split("."))
    try:
        return datetime.date(year, month, day)
    except ValueError:
        return None


def parse_timespan(text: str) -> datetime.timedelta | None:
    """``TimeSpan.TryParse`` for ``d*.hh:mm:ss`` moderator input.

    Accepts the standard .NET forms: a bare number (days), ``hh:mm``,
    ``hh:mm:ss`` and ``d.hh:mm``/``d.hh:mm:ss``. Returns ``None`` on anything
    else.
    """
    value = text.strip()
    if not value:
        return None
    negative = value.startswith("-")
    if negative:
        value = value[1:]

    days = 0
    if "." in value:
        head, _, tail = value.partition(".")
        if ":" not in tail or not head.isdigit():
            return None
        days = int(head)
        value = tail

    if ":" in value:
        parts = value.split(":")
        if len(parts) not in (2, 3):
            return None
        if not all(p.isdigit() for p in parts):
            return None
        hours, minutes = int(parts[0]), int(parts[1])
        seconds = int(parts[2]) if len(parts) == 3 else 0
        if minutes >= 60 or seconds >= 60:
            return None
        result = datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    else:
        if not value.isdigit():
            return None
        result = datetime.timedelta(days=days + int(value))

    return -result if negative else result
