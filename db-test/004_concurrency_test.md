# Конкурентная проверка Notification Worker

Этот тест нужно выполнять в двух независимых PostgreSQL-сессиях, потому что `FOR UPDATE SKIP LOCKED` имеет смысл только при реальной конкуренции транзакций.

Перед тестом должно существовать хотя бы одно уведомление со статусом `PENDING` и `available_at <= now()`.

## Session A

```sql
BEGIN;

SELECT id
FROM messaging.notifications
WHERE status = 'PENDING'
  AND available_at <= now()
ORDER BY available_at, id
FOR UPDATE SKIP LOCKED
LIMIT 1;

-- Не делайте COMMIT сразу.
-- Оставьте транзакцию открытой.
```

## Session B

Одновременно выполнить:

```sql
BEGIN;

SELECT id
FROM messaging.notifications
WHERE status = 'PENDING'
  AND available_at <= now()
ORDER BY available_at, id
FOR UPDATE SKIP LOCKED
LIMIT 1;
```

Если в таблице было только одно подходящее уведомление, Session B не должна получить ту же строку: она будет пропущена из-за блокировки Session A.

После проверки:

```sql
ROLLBACK;
```

в обеих сессиях.

## Реальная транзакция worker'а

В production worker должен выполнять захват и перевод строки в `PROCESSING` в одной транзакции:

```sql
BEGIN;

WITH claimed AS (
    SELECT id
    FROM messaging.notifications
    WHERE status = 'PENDING'
      AND available_at <= now()
    ORDER BY available_at, id
    FOR UPDATE SKIP LOCKED
    LIMIT 50
)
UPDATE messaging.notifications n
SET status = 'PROCESSING',
    attempts = n.attempts + 1,
    locked_at = now()
FROM claimed
WHERE n.id = claimed.id
RETURNING n.*;

COMMIT;
```

Отправка в Telegram после commit должна сопровождаться отдельным обновлением `SENT` или возвратом в `PENDING`/`FAILED` при ошибке. Это позволяет избежать долгой блокировки БД во время сетевого вызова.
