"""Application configuration.

Mirrors the original C# configuration stack:

* Individual environment variables always take precedence over the JSON blob
  (the original app registered ``AddEnvironmentVariables()`` after the JSON).

Config keys (env, highest precedence):
    DATABASE_URL                 asyncpg URL to ``core_db``
    DATABASE_URL_SYNC           sync URL for alembic (optional)
    PROXY_MANAGER_URL           proxy-manager base URL (for car_places only)
    TG_BOT_TOKEN                   Telegram bot token
    TG_BOT_ALLOWED_UPDATES         comma separated update types (default: Message)
    NOTIFICATION_POLL_INTERVAL  seconds between notification polls (default 5)
    NOTIFICATION_MAX_CONCURRENCY  semaphore for notification fetches (default 15)
    NOTIFICATION_MAX_RETRIES    seat-change retry attempts (default 5)
"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env(*names: str, default: str | None = None) -> str:
    for name in names:
        value = os.environ.get(name)
        if value is not None and value.strip() != "":
            return value
    if default is None:
        raise ValueError(
            f"No one of the environment variables {', '.join(names)} is set or non-empty"
        )
    return default


@dataclass(frozen=True)
class BotSettings:
    token: str = ""
    allowed_updates: tuple[str, ...] = ("Message",)

    @staticmethod
    def from_sources() -> BotSettings:
        token = _env("TG_BOT_TOKEN")
        updates_raw = _env("TG_BOT_ALLOWED_UPDATES", default="").strip()
        updates = tuple(updates_raw.split(",")) if updates_raw else ("Message",)
        return BotSettings(token=token, allowed_updates=updates)


@dataclass(frozen=True)
class DatabaseSettings:
    connection_string: str = ""
    sync_connection_string: str = ""

    @staticmethod
    def from_sources() -> DatabaseSettings:
        sync_conn = _env("DATABASE_URL", "DATABASE__CONNECTIONSTRING", default="")
        sync_override = _env(
            "DATABASE_URL_SYNC",
            "DATABASE__SESSIONCONNECTIONSTRING",
            default=sync_conn,
        )
        return DatabaseSettings(
            connection_string=sync_conn,
            sync_connection_string=sync_override,
        )


@dataclass(frozen=True)
class ProxySettings:
    proxy_manager_url: str = ""

    @classmethod
    def from_sources(cls) -> ProxySettings:
        return cls(proxy_manager_url=_env("PROXY_MANAGER_URL", default=""))


@dataclass(frozen=True)
class NotifierSettings:
    poll_interval: float = 5.0
    max_concurrency: int = 15
    max_retries: int = 5

    @classmethod
    def from_sources(cls) -> NotifierSettings:
        return cls(
            poll_interval=float(_env("NOTIFICATION_POLL_INTERVAL", default="5")),
            max_concurrency=int(_env("NOTIFICATION_MAX_CONCURRENCY", default="15")),
            max_retries=int(_env("NOTIFICATION_MAX_RETRIES", default="5")),
        )


@dataclass(frozen=True)
class Settings:
    bot: BotSettings
    database: DatabaseSettings
    proxy: ProxySettings
    notifier: NotifierSettings


def load_settings() -> Settings:
    return Settings(
        bot=BotSettings.from_sources(),
        database=DatabaseSettings.from_sources(),
        proxy=ProxySettings.from_sources(),
        notifier=NotifierSettings.from_sources(),
    )
