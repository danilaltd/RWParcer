-- name: get_subscriptions_for_user(user_id)
SELECT id, user_id, service_route_id, target_date, status, last_checked_at, next_check_at, last_notified_at, created_at
FROM monitoring.subscriptions WHERE user_id = :user_id AND status IN ('ACTIVE', 'PAUSED');

-- name: get_all_active_subscriptions()
SELECT id, user_id, service_route_id, target_date, status, last_checked_at, next_check_at, last_notified_at, created_at
FROM monitoring.subscriptions WHERE status IN ('ACTIVE', 'PAUSED');

-- name: get_subscription_by_id(subscription_id)^
SELECT id, user_id, service_route_id, target_date, status, last_checked_at, next_check_at, last_notified_at, created_at
FROM monitoring.subscriptions WHERE id = :subscription_id;

-- name: insert_subscription(id, user_id, service_route_id, target_date, status, next_check_at)!
INSERT INTO monitoring.subscriptions (id, user_id, service_route_id, target_date, status, next_check_at)
VALUES (:id, :user_id, :service_route_id, :target_date, :status, :next_check_at);

-- name: subscription_exists(user_id, service_route_id, target_date)$
SELECT (COUNT(*) > 0) FROM monitoring.subscriptions
WHERE user_id = :user_id AND service_route_id = :service_route_id AND target_date = :target_date AND status IN ('ACTIVE', 'PAUSED');

-- name: get_subscription_count(user_id)$
SELECT COUNT(*) FROM monitoring.subscriptions
WHERE user_id = :user_id AND status IN ('ACTIVE', 'PAUSED');

-- name: update_subscription_times(subscription_id, last_checked_at, next_check_at)!
UPDATE monitoring.subscriptions SET last_checked_at = :last_checked_at, next_check_at = :next_check_at
WHERE id = :subscription_id;

-- name: reset_subscription_check(subscription_id, now)!
UPDATE monitoring.subscriptions SET next_check_at = :now WHERE id = :subscription_id;

-- name: cancel_subscription(subscription_id)!
UPDATE monitoring.subscriptions SET status = 'CANCELLED' WHERE id = :subscription_id;

-- name: claim_due_subscriptions(now, limit)
SELECT id FROM monitoring.subscriptions
WHERE status = 'ACTIVE' AND (next_check_at IS NULL OR next_check_at <= :now)
ORDER BY next_check_at, id LIMIT :limit
FOR UPDATE SKIP LOCKED;

-- name: update_claimed_subscriptions_next_check(sub_ids, next_check_at)!
UPDATE monitoring.subscriptions SET next_check_at = :next_check_at WHERE id = ANY(:sub_ids::uuid[]);
