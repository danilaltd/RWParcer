-- Deterministic development/demo data.
-- Safe to apply only to a fresh database or after clearing the demo rows.

BEGIN;

INSERT INTO identity.roles (id, code, name)
VALUES
    (1, 'USER', 'User'),
    (2, 'MODERATOR', 'Moderator'),
    (3, 'ADMIN', 'Administrator');

INSERT INTO transport.providers (
    id, code, name, adapter_code, base_url
)
VALUES
    ('10000000-0000-0000-0000-000000000001', 'RW_BY', 'Белорусская железная дорога', 'rw_by', 'https://apicast.rw.by'),
    ('10000000-0000-0000-0000-000000000002', 'DEMO_BUS', 'Demo Bus Provider', 'demo_bus', 'https://example.invalid');

INSERT INTO identity.users (
    id,
    telegram_user_id,
    telegram_chat_id,
    username,
    display_name,
    status,
    max_subscriptions,
    min_subscription_interval_seconds,
    created_at,
    last_activity_at
)
VALUES
    ('20000000-0000-0000-0000-000000000001', 100000001, 100000001, 'ivan', 'Ivan Demo', 'ACTIVE', 5, 15, now(), now()),
    ('20000000-0000-0000-0000-000000000002', 100000002, 100000002, 'moderator', 'Moderator Demo', 'ACTIVE', 20, 10, now(), now()),
    ('20000000-0000-0000-0000-000000000003', 100000003, 100000003, 'blocked', 'Blocked Demo', 'BLOCKED', 5, 15, now(), now());

INSERT INTO identity.user_roles (user_id, role_id, assigned_by_user_id)
VALUES
    ('20000000-0000-0000-0000-000000000001', 1, NULL),
    ('20000000-0000-0000-0000-000000000002', 1, NULL),
    ('20000000-0000-0000-0000-000000000002', 2, NULL),
    ('20000000-0000-0000-0000-000000000002', 3, NULL),
    ('20000000-0000-0000-0000-000000000003', 1, NULL);

INSERT INTO transport.stops (
    id, provider_id, external_code, name, latitude, longitude
)
VALUES
    ('30000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', '2100000', 'Минск-Пассажирский', 53.892235, 27.548700),
    ('30000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000001', '2100001', 'Брест-Центральный', 52.100000, 23.700000),
    ('30000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000001', '2100002', 'Витебск', 55.190000, 30.200000),
    ('30000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000002', 'BUS-MIN', 'Минск Автовокзал', 53.900000, 27.560000),
    ('30000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000002', 'BUS-VIC', 'Витебск Автовокзал', 55.190500, 30.205000);

INSERT INTO transport.services (
    id, provider_id, transport_mode, external_number, service_type, display_name
)
VALUES
    ('40000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', 'TRAIN', '702Б', 'interregional_business', '702Б'),
    ('40000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000001', 'TRAIN', '703Б', 'interregional_business', '703Б'),
    ('40000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000002', 'BUS', '123', 'INTERCITY', 'Автобус 123');

INSERT INTO transport.service_routes (
    id,
    service_id,
    from_stop_id,
    to_stop_id,
    departure_time,
    arrival_time,
    duration_minutes,
    days_rule,
    days_exceptions,
    valid_from,
    valid_to
)
VALUES
    ('50000000-0000-0000-0000-000000000001',
     '40000000-0000-0000-0000-000000000001',
     '30000000-0000-0000-0000-000000000002',
     '30000000-0000-0000-0000-000000000001',
     '06:40:00', '10:00:00', 200, 'ежедневно', NULL, '2026-01-01', NULL),
    ('50000000-0000-0000-0000-000000000002',
     '40000000-0000-0000-0000-000000000002',
     '30000000-0000-0000-0000-000000000001',
     '30000000-0000-0000-0000-000000000002',
     '18:20:00', '21:50:00', 210, 'ежедневно', NULL, '2026-01-01', NULL),
    ('50000000-0000-0000-0000-000000000003',
     '40000000-0000-0000-0000-000000000003',
     '30000000-0000-0000-0000-000000000004',
     '30000000-0000-0000-0000-000000000005',
     '08:00:00', '11:30:00', 210, 'по будням', NULL, '2026-01-01', NULL);

INSERT INTO monitoring.subscriptions (
    id, user_id, service_route_id, target_date, status,
    last_checked_at, next_check_at, last_notified_at
)
VALUES
    ('60000000-0000-0000-0000-000000000001',
     '20000000-0000-0000-0000-000000000001',
     '50000000-0000-0000-0000-000000000001',
     CURRENT_DATE + 14, 'ACTIVE',
     now() - interval '2 minutes', now() - interval '1 minute', NULL),
    ('60000000-0000-0000-0000-000000000002',
     '20000000-0000-0000-0000-000000000001',
     '50000000-0000-0000-0000-000000000002',
     CURRENT_DATE + 20, 'PAUSED',
     now() - interval '1 hour', now() + interval '1 hour', NULL);

INSERT INTO monitoring.favorites (id, user_id, service_route_id)
VALUES
    ('61000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000001'),
    ('61000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000003');

INSERT INTO monitoring.availability_snapshots (
    id, subscription_id, checked_at
)
VALUES
    ('62000000-0000-0000-0000-000000000001', '60000000-0000-0000-0000-000000000001', now() - interval '10 minutes'),
    ('62000000-0000-0000-0000-000000000002', '60000000-0000-0000-0000-000000000001', now() - interval '2 minutes');

INSERT INTO monitoring.availability_snapshot_seats (
    snapshot_id, unit_type, unit_number, place_code
)
VALUES
    ('62000000-0000-0000-0000-000000000001', 'COUPE', '4', '12'),
    ('62000000-0000-0000-0000-000000000001', 'COUPE', '4', '14'),
    ('62000000-0000-0000-0000-000000000002', 'COUPE', '4', '14'),
    ('62000000-0000-0000-0000-000000000002', 'COUPE', '4', '16');

INSERT INTO messaging.notifications (
    id, user_id, subscription_id, notification_type, content, status, available_at
)
VALUES
    ('63000000-0000-0000-0000-000000000001',
     '20000000-0000-0000-0000-000000000001',
     '60000000-0000-0000-0000-000000000001',
     'SEATS_CHANGED',
     'Поезд 702Б: появились свободные места в купе №4.',
     'PENDING', now());

INSERT INTO messaging.messages (
    id, sender_user_id, receiver_user_id, content
)
VALUES
    ('64000000-0000-0000-0000-000000000001',
     '20000000-0000-0000-0000-000000000001',
     '20000000-0000-0000-0000-000000000002',
     'Проверка работы feedback.'),
    ('64000000-0000-0000-0000-000000000002',
     '20000000-0000-0000-0000-000000000002',
     '20000000-0000-0000-0000-000000000001',
     'Сообщение получено.');

INSERT INTO bot.conversation_sessions (
    user_id, current_command_code, init_state, context, last_input_date, expires_at
)
VALUES
    ('20000000-0000-0000-0000-000000000001',
     12, false,
     '{"selected_route_id":"50000000-0000-0000-0000-000000000001","step":"awaiting_date"}'::jsonb,
     CURRENT_DATE,
     now() + interval '30 minutes');

INSERT INTO audit.audit_log (
    id, actor_user_id, action_code, entity_schema, entity_table, entity_id,
    old_values, new_values, source, correlation_id
)
VALUES
    ('65000000-0000-0000-0000-000000000001',
     '20000000-0000-0000-0000-000000000001',
     'SUBSCRIPTION_CREATED', 'monitoring', 'subscriptions',
     '60000000-0000-0000-0000-000000000001',
     NULL,
     '{"status":"ACTIVE","target_date":"demo"}'::jsonb,
     'BOT',
     NULL),
    ('65000000-0000-0000-0000-000000000002',
     '20000000-0000-0000-0000-000000000002',
     'USER_BLOCKED', 'identity', 'users',
     '20000000-0000-0000-0000-000000000003',
     '{"status":"ACTIVE"}'::jsonb,
     '{"status":"BLOCKED"}'::jsonb,
     'ADMIN',
     NULL);

COMMIT;
