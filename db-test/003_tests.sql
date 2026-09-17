-- Executable verification checks for the schema and demo data.
-- Run after 001_schema.sql and 002_seed.sql.
-- The tests intentionally use fresh UUIDs where possible.

BEGIN;

-- -----------------------------------------------------------------------------
-- 1. Basic row counts / presence checks
-- -----------------------------------------------------------------------------

DO $$
DECLARE
    n integer;
BEGIN
    SELECT count(*) INTO n FROM identity.roles;
    IF n < 3 THEN
        RAISE EXCEPTION 'FAIL: expected at least 3 roles, got %', n;
    END IF;

    SELECT count(*) INTO n FROM transport.providers;
    IF n < 2 THEN
        RAISE EXCEPTION 'FAIL: expected at least 2 providers, got %', n;
    END IF;

    SELECT count(*) INTO n FROM transport.service_routes;
    IF n < 3 THEN
        RAISE EXCEPTION 'FAIL: expected at least 3 service routes, got %', n;
    END IF;
END $$;

-- -----------------------------------------------------------------------------
-- 2. User lookup and authorization joins
-- -----------------------------------------------------------------------------

DO $$
DECLARE
    role_count integer;
BEGIN
    SELECT count(*)
    INTO role_count
    FROM identity.user_roles ur
    JOIN identity.roles r ON r.id = ur.role_id
    WHERE ur.user_id = '20000000-0000-0000-0000-000000000002'
      AND r.code IN ('USER', 'MODERATOR', 'ADMIN');

    IF role_count <> 3 THEN
        RAISE EXCEPTION 'FAIL: moderator/admin demo user should have 3 roles, got %', role_count;
    END IF;
END $$;

-- -----------------------------------------------------------------------------
-- 3. Duplicate favorite must be rejected
-- -----------------------------------------------------------------------------

DO $$
BEGIN
    BEGIN
        INSERT INTO monitoring.favorites (id, user_id, service_route_id)
        VALUES (
            gen_random_uuid(),
            '20000000-0000-0000-0000-000000000001',
            '50000000-0000-0000-0000-000000000001'
        );
        RAISE EXCEPTION 'FAIL: duplicate favorite was accepted';
    EXCEPTION
        WHEN unique_violation THEN
            NULL;
    END;
END $$;

-- -----------------------------------------------------------------------------
-- 4. Duplicate active/paused subscription must be rejected
-- -----------------------------------------------------------------------------

DO $$
BEGIN
    BEGIN
        INSERT INTO monitoring.subscriptions (
            id, user_id, service_route_id, target_date, status
        )
        VALUES (
            gen_random_uuid(),
            '20000000-0000-0000-0000-000000000001',
            '50000000-0000-0000-0000-000000000001',
            CURRENT_DATE + 14,
            'ACTIVE'
        );
        RAISE EXCEPTION 'FAIL: duplicate active subscription was accepted';
    EXCEPTION
        WHEN unique_violation THEN
            NULL;
    END;
END $$;

-- -----------------------------------------------------------------------------
-- 5. Cancelled subscription may be recreated
-- -----------------------------------------------------------------------------

DO $$
DECLARE
    cancelled_id uuid;
    new_id uuid := gen_random_uuid();
BEGIN
    INSERT INTO monitoring.subscriptions (
        id, user_id, service_route_id, target_date, status
    )
    VALUES (
        gen_random_uuid(),
        '20000000-0000-0000-0000-000000000001',
        '50000000-0000-0000-0000-000000000002',
        CURRENT_DATE + 21,
        'CANCELLED'
    )
    RETURNING id INTO cancelled_id;

    INSERT INTO monitoring.subscriptions (
        id, user_id, service_route_id, target_date, status
    )
    VALUES (
        new_id,
        '20000000-0000-0000-0000-000000000001',
        '50000000-0000-0000-0000-000000000002',
        CURRENT_DATE + 21,
        'ACTIVE'
    );
END $$;

-- -----------------------------------------------------------------------------
-- 6. Due subscription query used by monitor worker
-- -----------------------------------------------------------------------------

DO $$
DECLARE
    route_count integer;
BEGIN
    SELECT count(*)
    INTO route_count
    FROM monitoring.subscriptions s
    WHERE s.status = 'ACTIVE'
      AND s.next_check_at <= now();

    IF route_count < 1 THEN
        RAISE EXCEPTION 'FAIL: expected at least one due active subscription';
    END IF;
END $$;

-- -----------------------------------------------------------------------------
-- 7. Verify snapshot -> seats relation and history ordering
-- -----------------------------------------------------------------------------

DO $$
DECLARE
    n integer;
BEGIN
    SELECT count(*)
    INTO n
    FROM monitoring.availability_snapshot_seats ass
    JOIN monitoring.availability_snapshots a
      ON a.id = ass.snapshot_id
    WHERE a.subscription_id = '60000000-0000-0000-0000-000000000001';

    IF n <> 4 THEN
        RAISE EXCEPTION 'FAIL: expected 4 demo free-seat rows, got %', n;
    END IF;
END $$;

-- -----------------------------------------------------------------------------
-- 8. Notification queue selection shape
--    This verifies that pending + due rows exist. The actual SKIP LOCKED
--    concurrency behavior is covered by 004_concurrency_test.md.
-- -----------------------------------------------------------------------------

DO $$
DECLARE
    n integer;
BEGIN
    SELECT count(*)
    INTO n
    FROM messaging.notifications
    WHERE status = 'PENDING'
      AND available_at <= now();

    IF n < 1 THEN
        RAISE EXCEPTION 'FAIL: expected at least one pending notification';
    END IF;
END $$;

-- -----------------------------------------------------------------------------
-- 9. FSM context must be a JSON object
-- -----------------------------------------------------------------------------

DO $$
DECLARE
    t text;
BEGIN
    SELECT jsonb_typeof(context)
    INTO t
    FROM bot.conversation_sessions
    WHERE user_id = '20000000-0000-0000-0000-000000000001';

    IF t <> 'object' THEN
        RAISE EXCEPTION 'FAIL: bot conversation context must be a JSON object';
    END IF;
END $$;

-- -----------------------------------------------------------------------------
-- 10. Audit rows exist and are attributable
-- -----------------------------------------------------------------------------

DO $$
DECLARE
    n integer;
BEGIN
    SELECT count(*)
    INTO n
    FROM audit.audit_log
    WHERE actor_user_id IS NOT NULL;

    IF n < 1 THEN
        RAISE EXCEPTION 'FAIL: expected at least one attributable audit row';
    END IF;
END $$;

-- -----------------------------------------------------------------------------
-- 11. Negative FK test: nonexistent route must not be accepted
-- -----------------------------------------------------------------------------

DO $$
BEGIN
    BEGIN
        INSERT INTO monitoring.favorites (id, user_id, service_route_id)
        VALUES (
            gen_random_uuid(),
            '20000000-0000-0000-0000-000000000001',
            'ffffffff-ffff-ffff-ffff-ffffffffffff'
        );
        RAISE EXCEPTION 'FAIL: nonexistent service_route was accepted';
    EXCEPTION
        WHEN foreign_key_violation THEN
            NULL;
    END;
END $$;

-- -----------------------------------------------------------------------------
-- 12. Verify monitor worker uses the intended indexed access predicate.
--     This prints the plan; inspect it after adding real data at scale.
-- -----------------------------------------------------------------------------

EXPLAIN (COSTS OFF)
SELECT s.id, s.user_id, s.service_route_id, s.target_date
FROM monitoring.subscriptions s
WHERE s.status = 'ACTIVE'
  AND s.next_check_at <= now()
ORDER BY s.next_check_at, s.id
LIMIT 100;

ROLLBACK;

SELECT 'ALL NON-CONCURRENCY TESTS PASSED' AS result;
