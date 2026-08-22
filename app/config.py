"""Application configuration.

Mirrors the original C# configuration stack:

* ``APPSETTINGS_JSON`` env var is parsed as JSON (equivalent to
  ``AppSettingsConfigurationExtensions.AddAppSettings``). If it is missing,
  individual environment variables are used.
* Individual environment variables always take precedence over the JSON blob
  (the original app registered ``AddEnvironmentVariables()`` after the JSON).

Config keys (env, highest precedence):
    DATABASE_URL                 asyncpg URL to ``core_db``
    DATABASE_URL_SYNC           sync URL for alembic (optional)
    PROXY_MANAGER_URL           proxy-manager base URL (for car_places only)
    BOT_TOKEN                   Telegram bot token
    BOT_ALLOWED_UPDATES         comma separated update types (default: Message)
    NOTIFICATION_POLL_INTERVAL  seconds between notification polls (default 5)
    NOTIFICATION_MAX_CONCURRENCY  semaphore for notification fetches (default 15)
    NOTIFICATION_MAX_RETRIES    seat-change retry attempts (default 5)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass


def _env(*names: str, default: str = "") -> str:
    for name in names:
        value = os.environ.get(name)
        if value is not None and value.strip() != "":
            return value
    return default


def _blob() -> dict:
    raw = os.environ.get("APPSETTINGS_JSON")
    if not raw or not raw.strip():
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(parsed, dict):
        return {}
    return parsed


@dataclass(frozen=True)
class BotSettings:
    token: str = ""
    allowed_updates: tuple[str, ...] = ("Message",)

    @staticmethod
    def from_sources(blob: dict) -> BotSettings:
        section = blob.get("BotSettings") or {}
        token = str(section.get("ApiToken") or section.get("Token") or "")
        token = _env("BOT_TOKEN", "BOTSETTINGS__APITOKEN", "BOTSETTINGS__TOKEN", default=token)
        updates_raw = section.get("AllowedUpdates")
        if isinstance(updates_raw, list):
            updates = tuple(str(item) for item in updates_raw)
        else:
            updates = ("Message",)
        configured = _env("BOT_ALLOWED_UPDATES", default="").strip()
        if configured:
            updates = tuple(item.strip() for item in configured.split(",") if item.strip())
        return BotSettings(token=token, allowed_updates=updates)


@dataclass(frozen=True)
class DatabaseSettings:
    connection_string: str = ""
    sync_connection_string: str = ""

    @staticmethod
    def from_sources(blob: dict) -> DatabaseSettings:
        section = blob.get("DatabaseSettings") or {}
        conn = str(section.get("ConnectionString") or "")
        sync_conn = str(section.get("SessionConnectionString") or "")
        conn_override = _env("DATABASE_URL", "DATABASE__CONNECTIONSTRING", default=conn)
        sync_override = _env(
            "DATABASE_URL_SYNC",
            "DATABASE__SESSIONCONNECTIONSTRING",
            default=sync_conn or conn_override,
        )
        return DatabaseSettings(
            connection_string=conn_override,
            sync_connection_string=sync_override,
        )


@dataclass(frozen=True)
class ProxySettings:
    proxy_manager_url: str = ""

    @classmethod
    def from_sources(cls, blob: dict) -> ProxySettings:
        section = blob.get("ProxySettings") or {}
        url = str(section.get("ProxyManagerUrl") or "")
        return cls(proxy_manager_url=_env("PROXY_MANAGER_URL", default=url or ""))


@dataclass(frozen=True)
class NotifierSettings:
    poll_interval: float = 5.0
    max_concurrency: int = 15
    max_retries: int = 5

    @classmethod
    def from_sources(cls, blob: dict) -> NotifierSettings:
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
    """Build :class:`Settings` from ``APPSETTINGS_JSON`` + env overrides."""
    blob = _blob()
    return Settings(
        bot=BotSettings.from_sources(blob),
        database=DatabaseSettings.from_sources(blob),
        proxy=ProxySettings.from_sources(blob),
        notifier=NotifierSettings.from_sources(blob),
    )
