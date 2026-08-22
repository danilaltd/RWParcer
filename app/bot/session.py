"""In-memory per-chat session, mirroring ``RWParcer/Models/UserSession.cs``.

The ``sessions`` table (see ``app/infrastructure/db/models.SessionRow``) is
the Postgres-backed FSM: a full snapshot of every ``BotSession`` is written
back after each update, exactly like ``PostgresSessionStore``.
"""

from __future__ import annotations

import datetime
from typing import Any

from app.bot.command_names import CommandNames


class BotSession:
    """Python twin of the C# ``UserSession``.

    * ``init_state`` is consumed on read (returns ``True`` once and then
      flips to ``False``) — the C# getter has this side effect.
    * ``date`` is the user's "last used" date, persisted as ``DateOnly``.
    """

    def __init__(
        self,
        current_command: CommandNames | None = None,
        init_state: bool | None = None,
        data: list[Any] | None = None,
        date: datetime.date | None = None,
    ) -> None:
        self._current_command = current_command
        # C# ``_initState`` defaults to ``true``.
        self._init_state = True if init_state is None else init_state
        self._data = list(data) if data is not None else []
        self._date = date if date is not None else datetime.date.today()

    @property
    def current_command(self) -> CommandNames | None:
        return self._current_command

    @property
    def init_state(self) -> bool:
        value = self._init_state
        self._init_state = False
        return value

    @property
    def data(self) -> list[Any]:
        return self._data

    @property
    def date(self) -> datetime.date:
        return self._date

    @date.setter
    def date(self, value: datetime.date) -> None:
        self._date = value

    def reset(self) -> None:
        """C# ``Reset()`` — clears command and data, keeps ``init_state``."""
        self._current_command = None
        self._data.clear()

    def set_command(self, command: CommandNames) -> None:
        """C# ``SetCommand()`` — sets command and re-arms ``init_state``."""
        self._current_command = command
        self._init_state = True