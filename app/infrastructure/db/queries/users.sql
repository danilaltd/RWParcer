-- name: get_user_by_id(id)^
SELECT id, telegram_user_id, telegram_chat_id, username, display_name, status, max_subscriptions, min_subscription_interval_seconds, last_activity_at, created_at, updated_at
FROM identity.users WHERE id = :id;

-- name: get_user_by_telegram_id(telegram_user_id)^
SELECT id, telegram_user_id, telegram_chat_id, username, display_name, status, max_subscriptions, min_subscription_interval_seconds, last_activity_at, created_at, updated_at
FROM identity.users WHERE telegram_user_id = :telegram_user_id;

-- name: user_exists(id)$
SELECT EXISTS(SELECT 1 FROM identity.users WHERE id = :id);

-- name: insert_user(id, telegram_user_id, telegram_chat_id, username, display_name, status, max_subscriptions, min_subscription_interval_seconds, last_activity_at)!
INSERT INTO identity.users (id, telegram_user_id, telegram_chat_id, username, display_name, status, max_subscriptions, min_subscription_interval_seconds, last_activity_at)
VALUES (:id, :telegram_user_id, :telegram_chat_id, :username, :display_name, :status, :max_subscriptions, :min_subscription_interval_seconds, :last_activity_at);

-- name: get_users_with_activity_since(cutoff_time)
SELECT id, telegram_user_id, telegram_chat_id, username, display_name, status, max_subscriptions, min_subscription_interval_seconds, last_activity_at, created_at, updated_at
FROM identity.users WHERE last_activity_at >= :cutoff_time;

-- name: get_users_by_ids(user_ids)
SELECT id, telegram_user_id, telegram_chat_id, username, display_name, status, max_subscriptions, min_subscription_interval_seconds, last_activity_at, created_at, updated_at
FROM identity.users WHERE id = ANY(:user_ids);

-- name: update_user_telegram_info(telegram_chat_id, username, display_name, last_activity_at, telegram_user_id)!
UPDATE identity.users SET telegram_chat_id = :telegram_chat_id, username = :username, display_name = :display_name, last_activity_at = :last_activity_at
WHERE telegram_user_id = :telegram_user_id;

-- name: update_user_min_interval(min_interval, user_id)!
UPDATE identity.users SET min_subscription_interval_seconds = :min_interval WHERE id = :user_id;

-- name: update_user_max_subscriptions(max_subscriptions, user_id)!
UPDATE identity.users SET max_subscriptions = :max_subscriptions WHERE id = :user_id;

-- name: update_user_status(status, user_id)!
UPDATE identity.users SET status = :status WHERE id = :user_id;

-- name: update_user_activity(now, user_id)!
UPDATE identity.users SET last_activity_at = :now WHERE id = :user_id;

-- name: system_has_users()$
SELECT EXISTS(SELECT 1 FROM identity.users LIMIT 1);