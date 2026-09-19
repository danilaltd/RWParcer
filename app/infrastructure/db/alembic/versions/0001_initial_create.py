"""initial create

Port of the EF Core ``20250530090726_InitialCreate`` schema (core_db tables
``users``/``subscriptions``/``favorites``/``messages``/``notifications``)
plus the bot FSM ``sessions`` table that lived in the separate
``sessions_db`` (``RWParcer/Migrations/20250525144407_InitialCreate.cs``).
The Python port keeps every table in the single ``core_db`` database.

Revision ID: 20250822_0001
Revises:
Create Date: 2025-08-22

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "20250822_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("is_moderator", sa.Boolean(), nullable=False),
        sa.Column("max_subscriptions", sa.BigInteger(), nullable=False),
        sa.Column("min_subscriptions_interval", sa.BigInteger(), nullable=False),
        sa.Column("is_blocked", sa.Boolean(), nullable=False),
        sa.Column("last_activity", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="p_k_users"),
    )
    op.create_table(
        "subscriptions",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("details", JSONB(), nullable=False),
        sa.Column("last_update", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_state", JSONB(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="p_k_subscriptions"),
    )
    op.create_index("i_x_subscriptions_user_id", "subscriptions", ["user_id"])
    op.create_table(
        "favorites",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("train_info", JSONB(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="p_k_favorites"),
    )
    op.create_index("i_x_favorites_user_id", "favorites", ["user_id"])
    op.create_table(
        "messages",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("sender_id", sa.Text(), nullable=False),
        sa.Column("receiver_id", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("sent_date", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="p_k_messages"),
    )
    op.create_index("i_x_messages_sender_id", "messages", ["sender_id"])
    op.create_index("i_x_messages_receiver_id", "messages", ["receiver_id"])
    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="p_k_notifications"),
    )
    op.create_index("i_x_notifications_user_id", "notifications", ["user_id"])
    op.create_table(
        "sessions",
        sa.Column("chat_id", sa.Text(), nullable=False),
        sa.Column("current_command", sa.Integer(), nullable=True),
        sa.Column("init_state", sa.Boolean(), nullable=False),
        sa.Column("data", sa.Text(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint("chat_id", name="p_k_sessions"),
    )


def downgrade() -> None:
    op.drop_table("sessions")
    op.drop_index("i_x_notifications_user_id", table_name="notifications")
    op.drop_table("notifications")
    op.drop_index("i_x_messages_receiver_id", table_name="messages")
    op.drop_index("i_x_messages_sender_id", table_name="messages")
    op.drop_table("messages")
    op.drop_index("i_x_favorites_user_id", table_name="favorites")
    op.drop_table("favorites")
    op.drop_index("i_x_subscriptions_user_id", table_name="subscriptions")
    op.drop_table("subscriptions")
    op.drop_table("users")
