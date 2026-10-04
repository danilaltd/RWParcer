"""SQLAlchemy ORM models mirroring the normalized PostgreSQL database schema."""

from __future__ import annotations

import datetime
import uuid  # noqa: TC003

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
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


class Base(MappedAsDataclass, DeclarativeBase):
    """Declarative base for all schemas."""


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------


class UserRow(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "identity"}

    telegram_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    telegram_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    username: Mapped[str | None] = mapped_column(Text)
    display_name: Mapped[str | None] = mapped_column(Text)
    last_activity_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), init=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        init=False,
    )

    id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        default=None,
    )
    status: Mapped[str] = mapped_column(Text, default="ACTIVE")
    max_subscriptions: Mapped[int] = mapped_column(Integer, default=5)
    min_subscription_interval_seconds: Mapped[int] = mapped_column(Integer, default=15)


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
        DateTime(timezone=True), server_default=func.now(), init=False
    )
    assigned_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), default=None)


# ---------------------------------------------------------------------------
# Transport
# ---------------------------------------------------------------------------


class ProviderRow(Base):
    __tablename__ = "providers"
    __table_args__ = {"schema": "transport"}

    code: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    adapter_code: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    base_url: Mapped[str | None] = mapped_column(Text)

    id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        default=None,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), init=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), init=False
    )


class StopRow(Base):
    __tablename__ = "stops"
    __table_args__ = (
        Index("stops_provider_external_code_uq", "provider_id", "external_code", unique=True),
        {"schema": "transport"},
    )

    provider_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    external_code: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[float | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[float | None] = mapped_column(Numeric(9, 6))

    id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        default=None,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), init=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), init=False
    )


class RouteRow(Base):
    __tablename__ = "routes"
    __table_args__ = (
        Index("routes_from_to_uq", "from_stop_id", "to_stop_id", unique=True),
        {"schema": "transport"},
    )

    from_stop_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    to_stop_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        default=None,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), init=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), init=False
    )


class ServiceRow(Base):
    __tablename__ = "services"
    __table_args__ = (
        Index(
            "services_provider_mode_number_route_uq",
            "provider_id",
            "transport_mode",
            "external_number",
            unique=True,
        ),
        {"schema": "transport"},
    )

    provider_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    route_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    transport_mode: Mapped[str] = mapped_column(Text, nullable=False)
    external_number: Mapped[str] = mapped_column(Text, nullable=False)
    service_type: Mapped[str | None] = mapped_column(Text)
    days_rule: Mapped[str | None] = mapped_column(Text)
    days_exceptions: Mapped[str | None] = mapped_column(Text)

    id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        default=None,
    )
    valid_from: Mapped[datetime.date | None] = mapped_column(
        Date, default=datetime.datetime.now(datetime.UTC).date()
    )
    valid_to: Mapped[datetime.date | None] = mapped_column(
        Date, default=(datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=365)).date()
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), init=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), init=False
    )


class ServiceRouteRow(Base):
    __tablename__ = "service_routes"
    __table_args__ = (
        Index("service_routes_business_uq", "service_id", "route_id", unique=True),
        {"schema": "transport"},
    )

    service_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    route_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    departure_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    arrival_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        default=None,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), init=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), init=False
    )


# ---------------------------------------------------------------------------
# Monitoring
# ---------------------------------------------------------------------------


class SubscriptionRow(Base):
    __tablename__ = "subscriptions"
    __table_args__ = {"schema": "monitoring"}

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    service_route_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    target_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    next_check_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))

    id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        default=None,
    )
    status: Mapped[str] = mapped_column(Text, default="ACTIVE")
    last_checked_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    last_notified_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), init=False
    )


class FavoriteRow(Base):
    __tablename__ = "favorites"
    __table_args__ = (
        Index("favorites_user_route_uq", "user_id", "service_route_id", unique=True),
        {"schema": "monitoring"},
    )

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    service_route_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        default=None,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), init=False
    )


class AvailabilitySnapshotRow(Base):
    __tablename__ = "availability_snapshots"
    __table_args__ = {"schema": "monitoring"}

    subscription_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    checked_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        default=None,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), init=False
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

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    subscription_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    available_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        default=None,
    )
    notification_type: Mapped[str] = mapped_column(Text, nullable=False, default="SEATS_CHANGED")
    status: Mapped[str] = mapped_column(Text, nullable=False, default="PENDING")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    sent_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), init=False
    )
    last_error: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), init=False
    )


class MessageRow(Base):
    __tablename__ = "messages"
    __table_args__ = {"schema": "messaging"}

    sender_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    receiver_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    content: Mapped[str] = mapped_column(Text, nullable=False)

    id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        default=None,
    )
    sent_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), init=False
    )
    read_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), default=None)


# ---------------------------------------------------------------------------
# Bot FSM state
# ---------------------------------------------------------------------------


class ConversationSessionRow(Base):
    __tablename__ = "conversation_sessions"
    __table_args__ = {"schema": "bot"}

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    current_command_code: Mapped[int | None] = mapped_column(Integer)
    last_input_date: Mapped[datetime.date | None] = mapped_column(Date)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), init=False
    )

    init_state: Mapped[bool] = mapped_column(Boolean, default=False)
    context: Mapped[dict] = mapped_column(JSONB, default_factory=dict)
    expires_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        default_factory=lambda: datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=3650),
    )


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------


class AuditLogRow(Base):
    __tablename__ = "audit_log"
    __table_args__ = {"schema": "audit"}

    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    action_code: Mapped[str] = mapped_column(Text, nullable=False)
    entity_schema: Mapped[str | None] = mapped_column(Text)
    entity_table: Mapped[str | None] = mapped_column(Text)
    entity_id: Mapped[str | None] = mapped_column(Text)
    old_values: Mapped[dict | None] = mapped_column(JSONB)
    new_values: Mapped[dict | None] = mapped_column(JSONB)
    correlation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))

    id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        default=None,
    )
    source: Mapped[str] = mapped_column(Text, nullable=False, default="BOT")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), init=False
    )
