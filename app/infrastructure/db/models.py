"""SQLAlchemy ORM models mirroring the EF ``AppDbContext``/``SessionDbContext`` maps.

Tables (snake_case names produced by EF's ``ToSnakeCase``):

=============== ============================================================
``users``       id (text), is_moderator, max_subscriptions,
                min_subscriptions_interval, is_blocked, last_activity
``subscriptions`` id (uuid), user_id, details (jsonb), last_update (timestamptz),
                last_state (jsonb)
``favorites``   id (uuid), user_id, train_info (jsonb)
``messages``    id, sender_id, receiver_id, content, sent_date (timestamptz)
``notifications`` id, user_id, content
``sessions``    chat_id, current_command, init_state, data, date  (bot FSM)
=============== ============================================================

JSONB columns store the raw JSON produced by the domain codecs (``json_codecs``),
so no SQLAlchemy ``TypeDecorator`` is needed — the repository layer converts.
"""

from __future__ import annotations

import datetime
import uuid

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Index, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for the whole schema."""


class UserRow(Base):
    """EF ``User`` entity, persisted in the ``users`` table."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    is_moderator: Mapped[bool] = mapped_column(Boolean, default=False)
    max_subscriptions: Mapped[int] = mapped_column(BigInteger, default=5)
    min_subscriptions_interval: Mapped[int] = mapped_column(BigInteger, default=15)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    last_activity: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
    )


class SubscriptionRow(Base):
    """SQL ``Subscription`` aggregate root."""

    __tablename__ = "subscriptions"
    __table_args__ = (Index("i_x_subscriptions_user_id", "user_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(Text)
    details: Mapped[dict] = mapped_column(JSONB)
    last_update: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    last_state: Mapped[list] = mapped_column(JSONB, default=list)


class FavoriteRow(Base):
    """SQL ``Favorite`` entity."""

    __tablename__ = "favorites"
    __table_args__ = (Index("i_x_favorites_user_id", "user_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(Text)
    train_info: Mapped[dict] = mapped_column(JSONB)


class MessageRow(Base):
    """SQL ``Message`` entity."""

    __tablename__ = "messages"
    __table_args__ = (
        Index("i_x_messages_sender_id", "sender_id"),
        Index("i_x_messages_receiver_id", "receiver_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    sender_id: Mapped[str] = mapped_column(Text)
    receiver_id: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    sent_date: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
    )


class NotificationRow(Base):
    """SQL ``Notification`` entity."""

    __tablename__ = "notifications"
    __table_args__ = (Index("i_x_notifications_user_id", "user_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)


class SessionRow(Base):
    """Bot FSM session (formerly a separate ``sessions_db``)."""

    __tablename__ = "sessions"

    chat_id: Mapped[str] = mapped_column(Text, primary_key=True)
    current_command: Mapped[int | None] = mapped_column(Integer)
    init_state: Mapped[bool] = mapped_column(Boolean, default=True)
    data: Mapped[str] = mapped_column(Text, default="")
    date: Mapped[datetime.date] = mapped_column(
        Date, default=func.current_date
    )
