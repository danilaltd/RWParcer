"""Plain-text converters, mirroring ``RWParcer/Converters/*.cs``."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.value_objects import MessageInfo, SubscriptionDetails, Train, UserInfo

_TRAIN_TYPE_RU = {
    "international": "Международные линии",
    "interregional_economy": "Межрегиональные линии экономкласса",
    "regional_economy": "Региональные линии экономкласса",
    "regional_business": "Региональные линии бизнес-класса",
    "interregional_business": "Межрегиональные линии бизнес-класса",
}


def convert_train(train: Train) -> str:
    """``TrainVOToStringConverter.Convert``."""
    route = f"{train.station_from.label} - {train.station_to.label}"
    times = f"{train.from_time:%H:%M}→{train.to_time:%H:%M}"
    duration_minutes = max(train.duration_minutes, 0)
    formatted_duration = f"{duration_minutes // 60:02d}:{duration_minutes % 60:02d}"
    number = f"№{train.train_number}"
    name = f"{train.title_station_from} - {train.title_station_to}"
    train_type = _TRAIN_TYPE_RU.get(train.train_type, train.train_type)
    train_days = f"Дни курсирования: {train.train_days}"
    if train.train_days_except:
        train_days += f", кроме {train.train_days_except}"
    return "\n".join((route, times, formatted_duration, number, name, train_type, train_days))


def user_to_string(user: UserInfo) -> str:
    """``UserVOToStringConverter.Convert``."""
    name = "Модератор" if user.is_moderator else "Пользователь"
    user_id = f"Id: {user.telegram_user_id}"
    link = "link: " + (
        f"@{user.username}"
        if user.username
        else f'<a href="tg://openmessage?user_id={user.telegram_user_id}">{user.display_name}</a>'
    )
    min_update_interval = f"Минимальный интервал обновления {user.min_update_interval}"
    max_subscriptions = f"Максимальное количество подписок {user.max_subscriptions}"
    is_blocked = "Заблокирован" if user.is_blocked else ""
    last_activity_body = (user.last_activity + datetime.timedelta(hours=3)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    last_activity = f"Последняя активность: {last_activity_body}"
    parts = [
        name,
        user_id,
        link,
        min_update_interval,
        max_subscriptions,
        is_blocked,
        last_activity,
    ]
    return "\n".join(part for part in parts if part)


def message_to_string(message: MessageInfo) -> str:
    """``MessageVOToStringConverter.Convert``."""
    time = (message.sent_date + datetime.timedelta(hours=3)).replace(microsecond=0)
    parts = [
        time.isoformat(sep=" "),
        f"from: {message.sender_id}",
        f"to: {message.receiver_id}",
        message.content,
    ]
    return "\n".join(part for part in parts if part)


def subscription_to_string(subscription: SubscriptionDetails) -> str:
    """``SubscriptionVOToStringConverter.Convert``."""
    date = subscription.date.strftime("%d.%m.%Y")
    return "\n".join((date, convert_train(subscription.train)))


__all__ = [
    "convert_train",
    "user_to_string",
    "message_to_string",
    "subscription_to_string",
]
