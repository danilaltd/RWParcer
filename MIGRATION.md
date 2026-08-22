# RWParcer: C# (.NET 9) → Python Migration

This document records how the original C# application was migrated to a Python
modular monolith under `app/`. Every piece of observable behavior (user-facing
strings, retry semantics, date rules, seat-diff logic, DB schema) is preserved.

## 1. Approach

| Decision | Choice |
|---|---|
| Architecture | Modular monolith, not microservices. The bot, application layer and infrastructure are Python packages in one process, sharing in-process calls. No REST contracts, queues or extra network hops between internal components. |
| Runtime | `app/__main__.py` is the composition root; entry `python -m app`. |
| Bot | `aiogram` 3.x **manual long-polling** — a `Bot.get_updates` loop in `app/bot/service.py` mirrors `BotService.StartReceiving`; no `Dispatcher`. |
| DB | `SQLAlchemy 2.0` (async) + `asyncpg` + `alembic`. One database `core_db` (the original had `core_db` + `sessions_db`; they are consolidated). |
| Session/FSM | PostgreSQL-backed custom storage `app/bot/storage.py` (`SessionStorage` + `BotSessionManager` over the `sessions` table); `MemoryStorage` and aiogram FSM are NOT used. |
| HTTP client | `httpx`, one shared client, 10 s timeout, proxy for car places only. |
| Config | `pydantic-settings`, reading `APPSETTINGS_JSON` (like `AppSettingsConfigurationExtensions`) + env overrides. |

## 2. Source layout vs. destination layout

| C# (original, kept untouched) | Python (new) |
|---|---|
| `RWParcerCore/Domain/` (entities, VOs, DTOs, mappers, repository interfaces) | `app/domain/` |
| `RWParcerCore/Application/UseCases/` | `app/application/services/` |
| `RWParcerCore/Infrastructure/Repositories/` + `AppDbContext` | `app/infrastructure/db/` |
| `RWParcerCore/Infrastructure/Repositories/RWParcer.cs` | `app/infrastructure/rw_client.py` |
| `RWParcerCore/Infrastructure/Converters/` (EF ValueConverters) | `app/domain/json_codecs.py` (exact same JSON shapes) |
| `RWParcerCore/Infrastructure/Services/NotificationBackgroundService.cs` | `app/application/notifier.py` |
| `RWParcerCore/InterfaceAdapters/Facades/Facade.cs` | `app/application/facade.py` |
| `RWParcer/Services/BotService.cs` + `CommandRouter` + Handlers | `app/bot/` — `service.py`, `router.py`, `handlers/*`, `context.py` |
| `RWParcer/Models/UserSession.cs`, `PostgresSessionStore.cs`, `SessionManager.cs` | `app/bot/session.py` + `app/bot/storage.py` |
| `Program.cs` (composition root) | `app/__main__.py` |

### 3. Domain mapping

| C# VO  | Python dataclass  | JSON keys |
|---|---|---|
| `StationVO(label, exp)` | `Station` (`label`, `exp`) | `label`, `exp` |
| `RouteVO(from, to)` | `Route` (`from`, `to`) | `{from: Station, to: Station}` (transient, never persisted) |
| `TrainVO(...)` | `Train` | `trainType`, `trainNumber`, `titleStationFrom`, `titleStationTo`, `stationFrom`, `stationTo`, `fromTime`, `toTime` (`HH:mm:ss` at UTC-3 — legacy quirk preserved), `trainDays`, `trainDaysExcept`, `durationMinutes` |
| `CarVO(type, number, freeSeats)` | `Car` (`car_type: CarType`, `number`, `free_seats`) | `type` (string id), `number`, `freeSeats` (array) |
| `SubscriptionVO(train, date)` | `Subscription` | `date` (`yyyy-MM-dd`), `train` |
| `UserVO(id, isModerator, maxSubscriptions, minSubscriptionsInterval, isBlocked, lastActivity)` | `UserInfo` | `id`, `isModerator`, `maxSubscriptions`, `minSubscriptionsInterval`, `isBlocked`, `lastActivity` |
| `MessageVO(senderId, receiverId, content, sentDate)` | `MessageInfo` | `senderId`, `receiverId`, `content`, `sentDate` (`yyyy-MM-ddTHH:mm:ss`) |
| `NotificationVO(userId, content)` | `NotificationItem` | transient |
| `CarType` enum | `CarType(str)` intenum-like constants | same numeric ids 1..6 |

## 4. Application layer mapping

Each C# *UseCase* becomes a method on the corresponding `app/application/services/*` module. All
`if (!IsUserRegistred) throw KeyNotFoundException`, `UpdateActivityAsync`,
`if (IsUserBanned) throw UnauthorizedAccessException`, and moderator-only
checks are expressed via small internal helpers that raise the same error types:

- `KeyNotFoundError` (→ `KeyNotFoundException`)
- `UnauthorizedError` (→ `UnauthorizedAccessException`)
- `InvalidOperationError` (`InvalidOperationException`)
- `OverflowError` reused for subscription-limit (matches C# `OverflowException`)

## 5. Infrastructure mapping

- `app/infrastructure/db/models.py` reproduces the alembic migration
  `20250530090726_InitialCreate` table-for-table: `users`, `favorites`,
  `subscriptions`, `notifications`, `messages`, plus `sessions`.
- Repositories in `app/infrastructure/db/repositories.py` mirror
  `UserRepository/FavoritesRepository/SubscriptionRepository/NotificationRepository/MessageRepository`.
- `app/infrastructure/rw_client.py` = `RWParcer.cs`:
  * **stations**: `GET https://pass.rw.by/ru/ajax/autocomplete/search/?term={prefix}` (no proxy)
  * **trains**: `GET https://apicast.rw.by/v1/rasp/ru/index/route?...` (no proxy)
  * **car places**: `GET https://apicast.rw.by/v1/rasp/ru/index/car_places?...` routed through `PROXY_MANAGER_URL` as `/proxy?url=<escaped>`
  * JSON edge cases: missing `routes` → `[]`; missing `tariffs` → skip car; missing `cars` → skip; `carNumberStr`/`emptyPlaces` null → skip.
- `app/infrastructure/proxy_client.py` and `http_client_factory.py`.
- `app/application/notifier.py` ports `NotificationBackgroundService`:
  * `SemaphoreSlim(15)` → `asyncio.Semaphore(15)`
  * prune `date < today` subscriptions and `continue`
  * per-sub: reload from DB, skip if missing
  * min-interval gating (`last_update` + user.min_subscriptions_interval)
  * `FindSeatChanges` (`AnyChangedSeats` / `HasCommonSeats`) semantics for the diff.
  * message: `dd.MM.yyyy` / `{from:Label} - {to:Label} / HH:mm→HH:mm` /
    `"Изменены места"|"Свободные места"`.
  * 5 retry attempts, `timeout` + HTTP + unknown kind catches.
- `app/bot/storage.py` is the Python twin of `PostgresSessionStore` +
  `SessionManager`: `SessionStorage.load()` reads the full `sessions` table,
  `SessionStorage.save_all()` upserts a full snapshot after every update, and
  `BotSessionManager` is the in-memory `GetOrAdd`-by-chat-id store.
  `sessions.data` is a JSON array of `{"Type": ..., "Data": ...}` objects —
  the exact shape `PostgresSessionStore.SaveAsync` produced via
  `SerializeToJson` — with `Train`/`Station`/`SubscriptionDetails`/`UserInfo`/
  `TimeSpan` (and list thereof) codecs in `app/bot/storage.py`.

Sessions were consolidated into `core_db.sessions` (the old `sessions_db`
is gone). Migrations run with `alembic -c alembic.ini upgrade head` inside the
container before `python -m app`; the URL comes from `DATABASE_URL`/
`DATABASE_URL_SYNC` (see `app/infrastructure/db/alembic/env.py`). CI runs
`ruff check app tests` + `.venv/bin/pytest -q` before any image build.

## 5. Behavior parity checkpoints (must keep identical)

1. Station prefix search flow (From/To), train search via indexed numbered list.
2. Subscribe/Unsubscribe/Reset flows with `InvalidOperation` vs `Overflow`
   messages: `"Подписка на дату {0} уже существует"`, `"Вы достигли лимита подписок"`, `"Подписка выполнена выполнена на ..."` (typo kept for fidelity).
3. Moderator flows (last users by span).
4. Notification message format (see §6).
5. 5-second poll loop of `PopNotifications` in `BotService`.

## 6. Notification format (from NotificationBackgroundService)

Reconstructed exact output for a "changed" notification:

```
📅 dd.MM.yyyy
StationFrom.Label - StationTo.Label
HH:mm→HH:mm
Изменены места
```
(empty-lines arrangement & "Свободные места" fallback — same in `notifier.py`)
On every non-ignored attempt the log line to stdout is `"Попытка {attempt}: Ошибка ..."` exactly as in C#.

## 7. Engine/OS parity

- Tests run on `pytest`/`pytest-asyncio`; lint via `ruff`.
- Build: repo-root `Dockerfile` (`python:3.12-slim`, `alembic upgrade head` then `python -m app`). Compose replaces the old .NET image.
- CI: `.github/workflows/main.yml` — `lint` (`ruff check app tests`) and `test` (`pytest -q`) jobs gate the image build/push.

## 8. Known deviations & assumptions

- `DateOnly` → `datetime.date`. Comparisons `date < today`, `today+3months` preserved.
- The old `SessionDbContext`/`sessions_db` is consolidated into `core_db.sessions`.
- `TrainVO.FromTime/ToTime` Python `datetime.time`, serialized for DB with the
  original UTC-3 quirk; from rw.by API it is derived the same way the C# mapper does.
- Any third-party proxy `proxy-manager` is reused as-is; this Python app is a
  HTTP client of it only for the `car_places` endpoint.
- The `.env.example` file is a template; secrets are not committed.