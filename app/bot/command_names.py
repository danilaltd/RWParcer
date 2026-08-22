"""Command state machine, mirroring ``RWParcer/CommandNames.cs``.

Values are the exact C# ordinal ints so the ``sessions.current_command``
integer column stays byte-compatible with the original schema.
"""

from __future__ import annotations

import enum


class CommandNames(enum.IntEnum):
    """C# ``enum CommandNames`` (declaration order preserved)."""

    START = 0
    MAIN_MENU_SELECT = 1
    FROM_SELECT = 2
    TO_SELECT = 3
    TRAIN_SELECT = 4
    TRAIN_MENU_SELECT = 5
    SUBSCRIBE_DATE_SELECT = 6
    SUBSCRIBE_ENTER_DATE = 7
    SUBSCRIBE_ENTER_DATE_RANGE = 8
    SUBSCRIBE_USE_LAST_DATE = 9
    UNSUBSCRIBE_DATE_SELECT = 10
    UNSUBSCRIBE_ENTER_DATE = 11
    UNSUBSCRIBE_ENTER_DATE_RANGE = 12
    UNSUBSCRIBE_USE_LAST_DATE = 13
    ADD_TO_FAVORITES = 14
    REMOVE_FROM_FAVORITES = 15
    FAVORITES_SELECT = 16
    SUBSCRIPTIONS_SELECT = 17
    SUBSCRIPTION_MENU_SELECT = 18
    UNSUBSCRIBE_SUBSCRIPTION = 19
    RESET_SUBSCRIPTION = 20
    MODERATOR_MENU_SELECT = 21
    SELECT_USER = 22
    MODERATOR_ENTER_SPAN = 23
    MODERATOR_SPAN_DAY = 24
    MODERATOR_SPAN_HOUR = 25
    MODERATOR_SPAN_MINUTE = 26
    MODERATOR_SPAN_SELECT = 27
    MANAGE_USER_MENU_SELECT = 28
    SEND_MESSAGE_ENTER_MESSAGE = 29
    CHANGE_USER_MIN_INTERVAL_LIMIT = 30
    CHANGE_USER_MAX_SUBSCRIPTION_LIMIT = 31
    BAN_USER = 32
    UNBAN_USER = 33
    PROMOTE_USER = 34
    DEMOTE_USER = 35
    VIEW_ALL_MESSAGES = 36
    VIEW_MESSAGES = 37
    GET_STATUS = 38
    FEEDBACK = 39
    UNKNOWN = 40


def command_name_by_value(value: int | None) -> CommandNames:
    """Map a stored integer back to a command, defaulting to ``UNKNOWN``."""
    try:
        return CommandNames(value) if value is not None else CommandNames.UNKNOWN
    except ValueError:
        return CommandNames.UNKNOWN