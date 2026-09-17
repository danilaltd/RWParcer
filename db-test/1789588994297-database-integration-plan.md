# План интеграции нормализованной схемы БД в приложение RWParcer

Этот документ содержит детальный, пошаговый план перехода приложения **RWParcer** со старой денормализованной структуры базы данных на новую нормализованную схему, разработанную в `db-test/`.

---

## 1. Аудит текущего состояния кода и разрывов

При переходе на схему `db-test` выявлены следующие изменения в контрактах данных и логике:

* **Идентификаторы пользователей:**
  * **Было:** Строковый `user_id` (Telegram `chat_id`) использовался во всей бизнес-логике и являлся первичным ключом в `users`.
  * **Стало:** Первичным ключом в `identity.users` является UUID (`id`). Telegram-идентификаторы `telegram_user_id` и `telegram_chat_id` хранятся независимо как `bigint`.
* **Способ хранения поездов:**
  * **Было:** Сериализованный `TrainVO` сохранялся внутри `JSONB` колонок в таблицах `subscriptions` и `favorites`.
  * **Стало:** Данные о поездах нормализуются в таблицы `transport.stops`, `transport.services` и `transport.service_routes`. Подписки и Избранное хранят ссылку `service_route_id` (UUID).
* **Свободные места:**
  * **Было:** Состояние свободных мест хранилось как массив JSONB `last_state` в таблице `subscriptions`.
  * **Стало:** Каждое свободное место записывается как строка в `monitoring.availability_snapshot_seats`, привязанная к `monitoring.availability_snapshots`.
* **Очередь уведомлений:**
  * **Было:** Очередь `notifications` очищалась через деструктивный `pop_all()` каждые 5 секунд.
  * **Стало:** Полноценный Transactional Outbox в `messaging.notifications` со статусами `PENDING`, `PROCESSING`, `SENT`, `FAILED` и конкурентным разбором через `SKIP LOCKED`.
* **Сессии бота (FSM):**
  * **Было:** Полная перезапись всей таблицы `sessions` при каждом обновлении любой сессии.
  * **Стало:** Точечный `UPSERT` в `bot.conversation_sessions` по UUID пользователя.

---

## 2. Маппинг старых сущностей на новую схему

| Старая таблица/поле | Новая таблица/поле | Тип данных | Правило маппинга |
|---|---|---|---|
| `users.id` | `identity.users.telegram_user_id` | `BIGINT` | Telegram ID пользователя |
| *(новое поле)* | `identity.users.telegram_chat_id` | `BIGINT` | Telegram ID чата |
| *(новое поле)* | `identity.users.id` | `UUID` | Внутренний идентификатор (Генерация на стороне БД) |
| `users.is_blocked` | `identity.users.status` | `TEXT` | `true` -> `'BLOCKED'`, `false` -> `'ACTIVE'` |
| `users.is_moderator` | `identity.user_roles` | Роли | Запись связи с `identity.roles` (ID=2, `'MODERATOR'`) |
| `subscriptions.details` (JSONB) | `transport.service_routes` | Нормализовано | Станции, поезд и расписание выносятся в справочники |
| `subscriptions.last_state` (JSON) | `monitoring.availability_snapshot_seats` | Строки | Каждое свободное место -> отдельная запись |
| `notifications` | `messaging.notifications` | Очередь | Статус по умолчанию `'PENDING'`, UUID первичный ключ |
| `sessions` | `bot.conversation_sessions` | JSONB | PK заменен на `user_id` (UUID), данные FSM в `context` |

---

## 3. Изменяемые и создаваемые файлы проекта

```text
app/
├── domain/
│   ├── entities.py             <-- (Изменение) Обновление моделей User, Subscription, Favorite
│   └── protocols.py            <-- (Изменение) Обновление сигнатур репозиториев
├── application/
│   ├── notifier.py             <-- (Изменение) Перенос наnext_check_at, нормализованные снимки
│   ├── services/
│   │   ├── users.py            <-- (Изменение) Резолв Telegram ID -> UUID, проверка статуса/ролей
│   │   ├── subscriptions.py    <-- (Изменение) Интеграция с get_or_create_service_route
│   │   ├── favorites.py        <-- (Изменение) Перевод на реляционные связи по UUID
│   │   ├── feedback.py         <-- (Изменение) Использование UUID отправителя/получателя
│   │   └── notifications.py    <-- (Изменение) Transactional Outbox отправка уведомлений
│   └── facade.py               <-- (Изменение) Обновление проксирующих методов бизнес-логики
├── infrastructure/
│   └── db/
│       ├── models.py           <-- (Замена) Описание SQLAlchemy моделей для новой схемы (с schemas)
│       └── repositories.py     <-- (Замена) Новые реализации репозиториев на чистом SQL
├── bot/
│   ├── service.py              <-- (Изменение) Добавление Middleware-резолвера пользователя, старт/стоп
│   ├── context.py              <-- (Изменение) Изменение сигнатур, переход с chat_id на UUID в FSM
│   └── storage.py              <-- (Замена) Реализация FSM поверх bot.conversation_sessions с UPSERT
```

---

## 4. Слой идентификации и авторизации пользователя

### 4.1. Резолв пользователя на границе системы
При получении события в `BotService._on_update`, до запуска роутера команд, приложение выполняет резолв пользователя.

**SQL запрос в `UserRepository.resolve_user`:**
```sql
INSERT INTO identity.users (
    telegram_user_id, 
    telegram_chat_id, 
    status, 
    max_subscriptions, 
    min_subscription_interval_seconds, 
    last_activity_at
)
VALUES (
    :telegram_user_id, 
    :telegram_chat_id, 
    'ACTIVE', 
    5, 
    15, 
    now()
)
ON CONFLICT (telegram_user_id) 
DO UPDATE SET
    telegram_chat_id = EXCLUDED.telegram_chat_id,
    last_activity_at = now()
RETURNING id, status;
```

### 4.2. Авторизация на уровне Use Cases (Бизнес-правила)
Каждый Use Case в `app/application/services/` принимает внутренний `user_id` (UUID). Первым шагом в декораторе или общем хелпере выполняется проверка прав.

**SQL запрос проверки блокировки и ролей:**
```sql
SELECT u.status, array_agg(r.code) as roles
FROM identity.users u
LEFT JOIN identity.user_roles ur ON ur.user_id = u.id
LEFT JOIN identity.roles r ON r.id = ur.role_id
WHERE u.id = :user_id
GROUP BY u.id, u.status;
```

**Правила авторизации:**
* Если `status == 'BLOCKED'` -> Выбросить `UnauthorizedError("User is blocked")`.
* Если требуется роль модератора (например, в `moderator.py`) -> Проверить наличие `'MODERATOR'` или `'ADMIN'` в массиве `roles`. Если отсутствует -> Выбросить `UnauthorizedError`.

---

## 5. Регистрация транспортного справочника (Идемпотентный Upsert)

При поиске поезда или оформлении подписки данные от API нормализуются и регистрируются в БД. Метод `get_or_create_service_route` гарантирует уникальность записей.

### 5.1. Порядок выполнения транзакции
Все шаги выполняются внутри единого блока `BEGIN ... COMMIT` на уровне `TransportRepository`:

1. **Регистрация провайдера (если отсутствует):**
   ```sql
   INSERT INTO transport.providers (code, name, adapter_code, is_active)
   VALUES ('RW_BY', 'Белорусская железная дорога', 'rw_by', true)
   ON CONFLICT (code) DO UPDATE SET is_active = true
   RETURNING id;
   ```
2. **Upsert Станции отправления и прибытия (выполняется параллельно для обеих):**
   ```sql
   INSERT INTO transport.stops (provider_id, external_code, name)
   VALUES (:provider_id, :external_code, :name)
   ON CONFLICT (provider_id, external_code) 
   DO UPDATE SET name = EXCLUDED.name
   RETURNING id;
   ```
3. **Upsert Транспортной службы (поезда):**
   ```sql
   INSERT INTO transport.services (provider_id, transport_mode, external_number, service_type, display_name)
   VALUES (:provider_id, 'TRAIN', :external_number, :service_type, :external_number)
   ON CONFLICT (provider_id, transport_mode, external_number)
   DO UPDATE SET service_type = EXCLUDED.service_type
   RETURNING id;
   ```
4. **Upsert Маршрута службы (привязка расписания):**
   Для service_routes отсутствует стабильный external_route_id у провайдера.

   В рамках текущей бизнес-модели уникальным идентификатором маршрута считается комбинация:

   (service_id, from_stop_id, to_stop_id)

   Не использовать departure_time, arrival_time, days_rule и valid_from/valid_to как часть идентификатора маршрута.

   При регистрации маршрута выполнять:
   
   ```sql
   INSERT INTO transport.service_routes (
      service_id,
      from_stop_id,
      to_stop_id,
      departure_time,
      arrival_time,
      duration_minutes,
      days_rule,
      valid_from,
      valid_to
   )
   VALUES (...)
   ON CONFLICT (service_id, from_stop_id, to_stop_id)
   DO UPDATE SET
      departure_time = EXCLUDED.departure_time,
      arrival_time = EXCLUDED.arrival_time,
      duration_minutes = EXCLUDED.duration_minutes,
      days_rule = EXCLUDED.days_rule,
      valid_from = EXCLUDED.valid_from,
      valid_to = EXCLUDED.valid_to
   RETURNING id;
   ```

---

## 6. Логика подписок и избранного

### 6.1. Создание подписки
**Граница транзакции:** `BEGIN` на уровне `subscriptions_service.subscribe`.
1. Проверить лимит подписок:
   ```sql
   SELECT count(*) FROM monitoring.subscriptions 
   WHERE user_id = :user_id AND status IN ('ACTIVE', 'PAUSED');
   ```
2. Проверить лимит пользователя:
   ```sql
   SELECT max_subscriptions FROM identity.users WHERE id = :user_id;
   ```
3. Записать подписку:
   ```sql
   INSERT INTO monitoring.subscriptions (user_id, service_route_id, target_date, status, next_check_at)
   VALUES (:user_id, :service_route_id, :target_date, 'ACTIVE', now())
   ON CONFLICT (user_id, service_route_id, target_date) WHERE status IN ('ACTIVE', 'PAUSED')
   DO NOTHING; -- Идемпотентность
   ```
4. Записать аудит в этой же транзакции:
   ```sql
   INSERT INTO audit.audit_log (actor_user_id, action_code, entity_schema, entity_table, entity_id, source)
   VALUES (:user_id, 'SUBSCRIPTION_CREATED', 'monitoring', 'subscriptions', :subscription_id, 'BOT');
   ```
5. `COMMIT`.

---

## 7. Воркер мониторинга (Monitor Worker)

Воркер `Notifier` запускается в фоновом цикле в единственном или нескольких экземплярах.

### 7.1. Захват задач на проверку (Concurrency & Locking)
Чтобы избежать одновременной проверки одной подписки несколькими воркерами, выборка и блокировка производятся атомарно в транзакции.

```sql
BEGIN;

-- Шаг 1: Получаем ID подписок, которые подошли по времени, и лочим их строки
WITH target_subs AS (
    SELECT id
    FROM monitoring.subscriptions
    WHERE status = 'ACTIVE'
      AND (next_check_at IS NULL OR next_check_at <= now())
    ORDER BY next_check_at, id
    FOR UPDATE SKIP LOCKED
    LIMIT 10
)
-- Шаг 2: Временно отодвигаем время следующей проверки вперед (на 5 минут), чтобы другие воркеры их не трогали
UPDATE monitoring.subscriptions s
SET next_check_at = now() + interval '5 minutes'
FROM target_subs
WHERE s.id = target_subs.id
RETURNING s.id, s.user_id, s.service_route_id, s.target_date;

COMMIT;
```
*Если воркер упадет во время обработки, через 5 минут подписка снова станет доступна для захвата.*

### 7.2. Логика проверки и сравнения снимков свободных мест
availability_snapshots хранит успешные снимки состояния доступности, а не каждую проверку API.

При первой успешной проверке создаётся initial snapshot.

При последующих проверках:
- если состояние доступности не изменилось — новый snapshot не создаётся;
- обновляются только last_checked_at и next_check_at;
- если состояние изменилось — создаётся новый snapshot с текущим набором мест и создаётся notification.

Таким образом:
last_checked_at отражает частоту polling,
availability_snapshots отражает историю изменений состояния.

Это сделано намеренно для поддержки polling с интервалом 5–60 секунд и предотвращения чрезмерного роста таблицы snapshots.
Для каждой выбранной подписки:
1. Выполняется запрос к API `apicast.rw.by` (через прокси).
2. Загружается последний снимок мест из БД:
   ```sql
   SELECT ass.unit_type, ass.unit_number, ass.place_code
   FROM monitoring.availability_snapshots snap
   JOIN monitoring.availability_snapshot_seats ass ON ass.snapshot_id = snap.id
   WHERE snap.subscription_id = :subscription_id
   ORDER BY snap.checked_at DESC
   LIMIT 1; -- Последний снимок
   ```
3. **Сравнение (в памяти приложения):** Сравниваются множества `(unit_type, unit_number, place_code)`. Находятся:
   * **Добавленные места** (появились в ответе API, не было в БД).
   * **Удаленные места** (были в БД, пропали в ответе API).
4. Если изменения найдены:
   * **Начало транзакции (DB Write):**
     ```sql
     BEGIN;

     -- 1. Запись нового снимка
     INSERT INTO monitoring.availability_snapshots (id, subscription_id, checked_at)
     VALUES (:snapshot_id, :subscription_id, now())
     RETURNING id;

     -- 2. Запись мест в снимке
     INSERT INTO monitoring.availability_snapshot_seats (snapshot_id, unit_type, unit_number, place_code)
     VALUES (:snapshot_id, :type, :num, :seat);

     -- 3. Добавление в Outbox-очередь уведомлений
     INSERT INTO messaging.notifications (user_id, subscription_id, notification_type, content, status, available_at)
     VALUES (:user_id, :subscription_id, 'SEATS_CHANGED', :diff_text, 'PENDING', now());

     -- 4. Обновление подписки (расчет реального следующего времени проверки)
     UPDATE monitoring.subscriptions
     SET last_checked_at = now(),
         next_check_at = now() + (:user_interval_seconds * interval '1 second')
     WHERE id = :subscription_id;

     COMMIT;
     ```
5. Если изменений не было:
   * Обновляется только время следующей проверки:
     ```sql
     UPDATE monitoring.subscriptions
     SET last_checked_at = now(),
         next_check_at = now() + (:user_interval_seconds * interval '1 second')
     WHERE id = :subscription_id;
     ```

---

## 8. Transactional Outbox & Notification Worker

### 8.1. Выборка из очереди уведомлений (`messaging.notifications`)
Отправщик уведомлений в боте работает независимо. Каждые 5 секунд он забирает пачку сообщений:

```sql
BEGIN;

-- Захватываем свободные сообщения
WITH claimed AS (
    SELECT id
    FROM messaging.notifications
    WHERE status = 'PENDING'
      AND available_at <= now()
      AND attempts < 5
    ORDER BY available_at, id
    FOR UPDATE SKIP LOCKED
    LIMIT 50
)
-- Переводим в статус PROCESSING, чтобы никто больше их не взял
UPDATE messaging.notifications n
SET status = 'PROCESSING',
    locked_at = now(),
    attempts = n.attempts + 1
FROM claimed
WHERE n.id = claimed.id
RETURNING n.id, n.user_id, n.content;

COMMIT;
```

### 8.2. Отправка в Telegram
Для каждой записи из пачки (выполняется **вне транзакции БД**, чтобы избежать долгих сетевых блокировок):
1. Выполняется отправка сообщения в Telegram API.
2. **Результат успешен:**
   ```sql
   UPDATE messaging.notifications
   SET status = 'SENT', sent_at = now()
   WHERE id = :id;
   ```
3. **Сбой отправки (ошибка сети/блок бота пользователем):**
   * Если пользователь заблокировал бота -> деактивировать подписки пользователя.
   * Иначе (сетевой сбой) -> Вернуть в `PENDING` с экспоненциальным сдвигом времени повтора:
     ```sql
     UPDATE messaging.notifications
     SET status = 'PENDING',
         available_at = now() + (power(2, attempts) * interval '10 seconds'),
         last_error = :error_text
     WHERE id = :id;
     ```

### 8.3. Механизм самовосстановления зависших задач (Recovery)
Если процесс воркера упал в момент отправки, сообщения останутся в статусе `PROCESSING`. Каждые 5 минут запускается фоновый SQL-запрос восстановления:

```sql
UPDATE messaging.notifications
SET status = 'PENDING',
    available_at = now() + interval '1 minute',
    last_error = 'Worker timeout recovery'
WHERE status = 'PROCESSING'
  AND locked_at <= now() - interval '5 minutes';
```

---

## 9. Система аудита (Audit Logging)

Логированию подлежат критические операции. Записи создаются в рамках той же транзакции, которая изменяет бизнес-сущность.

```sql
INSERT INTO audit.audit_log (
    actor_user_id, 
    action_code, 
    entity_schema, 
    entity_table, 
    entity_id, 
    old_values, 
    new_values, 
    source
)
VALUES (
    :actor_uuid, 
    :action, 
    :schema, 
    :table, 
    :id, 
    :old_val::jsonb, 
    :new_val::jsonb, 
    'BOT'
);
```

**События аудита:**
* `USER_CREATED` / `USER_BLOCKED` / `USER_UNBLOCKED`
* `ROLE_ASSIGNED` / `ROLE_REMOVED`
* `SUBSCRIPTION_CREATED` / `SUBSCRIPTION_CANCELLED` / `SUBSCRIPTION_PAUSED`
* `FAVORITE_ADDED` / `FAVORITE_REMOVED`

---

## 10. План верификации и тестирования

### 10.1. SQL тесты (Базовый DDL и триггеры)
* Выполнить тестовый скрипт `db-test/003_tests.sql` для проверки констрейнтов.
* Проверить автоматическое срабатывание триггера `updated_at` на таблицах `identity.users` и `transport.stops`.

### 10.2. Тесты конкурентности (Concurrency Tests)
* Запустить два экземпляра скрипта, эмулирующих захват задач в воркере:
  * Сессия 1 делает `SELECT FOR UPDATE SKIP LOCKED` и держит транзакцию открытой.
  * Сессия 2 делает аналогичный запрос. Ожидаемый результат: Сессия 2 получает пустой массив (или другие строки), но не зависает в ожидании разблокировки.

### 10.3. Интеграционные тесты приложения (Python-уровень)
* Проверить полный цикл:
  1. `BotService` получает Telegram ID -> резолвит UUID.
  2. Запрос поиска поезда -> upsert в справочники `transport.*`.
  3. Оформление подписки -> создание записи в `subscriptions` и запись в `audit_log`.
  4. Запуск `Notifier` -> обнаружение изменений -> генерация `availability_snapshots` и outbox-уведомлений.
  5. Запуск `Notification Worker` -> отправка в симулированный бот -> обновление статуса на `SENT`.

---

## 11. Пошаговый порядок выполнения работ (Rollout)

Чтобы приложение оставалось работоспособным на промежуточных этапах, интеграцию следует выполнять строго по шагам:

1. **Шаг 1: Подготовка БД**
   * Применить схему DDL из `db-test/001_schema.sql` на инстансе PostgreSQL.
   * Запустить `002_seed.sql` для инициализации ролей и провайдеров.
2. **Шаг 2: Обновление моделей данных в приложении**
   * Переписать SQLAlchemy-модели в `app/infrastructure/db/models.py`, настроив schemas.
   SQLAlchemy ORM сохраняется на этапе текущей миграции, поскольку он уже используется приложением.
   Не выполнять в рамках этой итерации переход на raw SQL / отказ от ORM.
   Отказ от ORM является отдельной будущей архитектурной итерацией.
   При этом новая бизнес-модель и структура repositories должны быть организованы так, чтобы дальнейший отказ от ORM не требовал изменения application/domain layers.
3. **Шаг 3: Реализация UserRepository и Слоеной авторизации**
   * Обновить репозиторий пользователей, добавить методы резолва ID и проверки ролей.
   * Написать юнит-тесты на авторизацию.
4. **Шаг 4: Интеграция транспортных справочников**
   * Реализовать `TransportRepository` и логику `get_or_create_service_route`.
5. **Шаг 5: Перевод FSM на новые рельсы**
   * Обновить `bot.conversation_sessions` репозиторий и адаптер сессий в `app/bot/storage.py`.
6. **Шаг 6: Миграция подписок и избранного**
   * Переписать методы создания/удаления подписок и избранного под реляционные FK.
7. **Шаг 7: Обновление Monitor Worker и Notification Worker**
   * Интегрировать `SKIP LOCKED` алгоритмы и обработку очередей.
8. **Шаг 8: Включение системы аудита**
   * Настроить логирование изменений во всех репозиториях.
9. **Шаг 9: Финальное приёмочное тестирование**
   * Запуск сквозного прогона сценария.
