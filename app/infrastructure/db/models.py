"""SQLAlchemy ORM models mirroring the normalized PostgreSQL database schema."""

from __future__ import annotations

import datetime
import json
import uuid
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    Text,
    Time,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for all schemas."""


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------


class UserRow(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "identity"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    telegram_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    username: Mapped[str | None] = mapped_column(Text)
    display_name: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, default="ACTIVE")
    max_subscriptions: Mapped[int] = mapped_column(Integer, default=5)
    min_subscription_interval_seconds: Mapped[int] = mapped_column(Integer, default=15)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
    )
    last_activity_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))


class RoleRow(Base):
    __tablename__ = "roles"
    __table_args__ = {"schema": "identity"}

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    code: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)


class UserRoleRow(Base):
    __tablename__ = "user_roles"
    __table_args__ = {"schema": "identity"}

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    role_id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    assigned_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )
    assigned_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))


# ---------------------------------------------------------------------------
# Transport
# ---------------------------------------------------------------------------


class ProviderRow(Base):
    __tablename__ = "providers"
    __table_args__ = {"schema": "transport"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    adapter_code: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    base_url: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )


class StopRow(Base):
    __tablename__ = "stops"
    __table_args__ = (
        Index("stops_provider_external_code_uq", "provider_id", "external_code", unique=True),
        {"schema": "transport"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    external_code: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[float | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[float | None] = mapped_column(Numeric(9, 6))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )


class ServiceRow(Base):
    __tablename__ = "services"
    __table_args__ = (
        Index(
            "services_provider_mode_number_uq",
            "provider_id",
            "transport_mode",
            "external_number",
            unique=True,
        ),
        {"schema": "transport"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    transport_mode: Mapped[str] = mapped_column(Text, nullable=False)
    external_number: Mapped[str] = mapped_column(Text, nullable=False)
    service_type: Mapped[str | None] = mapped_column(Text)
    display_name: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )


class ServiceRouteRow(Base):
    __tablename__ = "service_routes"
    __table_args__ = (
        Index(
            "service_routes_business_uq", "service_id", "from_stop_id", "to_stop_id", unique=True
        ),
        {"schema": "transport"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    from_stop_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    to_stop_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    departure_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    arrival_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    days_rule: Mapped[str | None] = mapped_column(Text)
    days_exceptions: Mapped[str | None] = mapped_column(Text)
    valid_from: Mapped[datetime.date | None] = mapped_column(Date)
    valid_to: Mapped[datetime.date | None] = mapped_column(Date)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )


# ---------------------------------------------------------------------------
# Monitoring
# ---------------------------------------------------------------------------


class SubscriptionRow(Base):
    __tablename__ = "subscriptions"
    __table_args__ = {"schema": "monitoring"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    service_route_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    target_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(Text, default="ACTIVE")
    last_checked_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    next_check_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    last_notified_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )


class FavoriteRow(Base):
    __tablename__ = "favorites"
    __table_args__ = (
        Index("favorites_user_route_uq", "user_id", "service_route_id", unique=True),
        {"schema": "monitoring"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    service_route_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )


class AvailabilitySnapshotRow(Base):
    __tablename__ = "availability_snapshots"
    __table_args__ = {"schema": "monitoring"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    checked_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )


class AvailabilitySnapshotSeatRow(Base):
    __tablename__ = "availability_snapshot_seats"
    __table_args__ = {"schema": "monitoring"}

    snapshot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    unit_type: Mapped[str] = mapped_column(Text, primary_key=True)
    unit_number: Mapped[str] = mapped_column(Text, primary_key=True)
    place_code: Mapped[str] = mapped_column(Text, primary_key=True)


# ---------------------------------------------------------------------------
# Messaging
# ---------------------------------------------------------------------------


class NotificationRow(Base):
    __tablename__ = "notifications"
    __table_args__ = {"schema": "messaging"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    subscription_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    notification_type: Mapped[str] = mapped_column(Text, nullable=False, default="SEATS_CHANGED")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="PENDING")
    available_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )


class MessageRow(Base):
    __tablename__ = "messages"
    __table_args__ = {"schema": "messaging"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    receiver_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )
    read_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))


# ---------------------------------------------------------------------------
# Bot FSM state
# ---------------------------------------------------------------------------


class ConversationSessionRow(Base):
    __tablename__ = "conversation_sessions"
    __table_args__ = {"schema": "bot"}

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    current_command_code: Mapped[int | None] = mapped_column(Integer)
    init_state: Mapped[bool] = mapped_column(Boolean, default=False)
    context: Mapped[dict] = mapped_column(JSONB, default=dict)
    last_input_date: Mapped[datetime.date | None] = mapped_column(Date)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )
    expires_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))

    def __init__(self, chat_id: str | uuid.UUID | None = None, **kwargs: Any) -> None:
        if chat_id is not None:
            if isinstance(chat_id, uuid.UUID):
                kwargs["user_id"] = chat_id
            else:
                try:
                    kwargs["user_id"] = uuid.UUID(chat_id)
                except ValueError:
                    kwargs["user_id"] = uuid.uuid5(uuid.NAMESPACE_DNS, str(chat_id))
        if "current_command" in kwargs:
            kwargs["current_command_code"] = kwargs.pop("current_command")
        if "data" in kwargs:
            d = kwargs.pop("data")
            kwargs["context"] = {"data": json.loads(d) if isinstance(d, str) else d}
        if "date" in kwargs:
            kwargs["last_input_date"] = kwargs.pop("date")
        super().__init__(**kwargs)

    @property
    def chat_id(self) -> str:
        return str(self.user_id)

    @chat_id.setter
    def chat_id(self, value: str | uuid.UUID) -> None:
        if isinstance(value, uuid.UUID):
            self.user_id = value
        else:
            try:
                self.user_id = uuid.UUID(value)
            except ValueError:
                self.user_id = uuid.uuid5(uuid.NAMESPACE_DNS, str(value))


SessionRow = ConversationSessionRow


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------


class AuditLogRow(Base):
    __tablename__ = "audit_log"
    __table_args__ = {"schema": "audit"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    action_code: Mapped[str] = mapped_column(Text, nullable=False)
    entity_schema: Mapped[str | None] = mapped_column(Text)
    entity_table: Mapped[str | None] = mapped_column(Text)
    entity_id: Mapped[str | None] = mapped_column(Text)
    old_values: Mapped[dict | None] = mapped_column(JSONB)
    new_values: Mapped[dict | None] = mapped_column(JSONB)
    source: Mapped[str] = mapped_column(Text, nullable=False, default="BOT")
    correlation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )
