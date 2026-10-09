-- name: reset_stuck_processing_notifications(stuck_cutoff)!
UPDATE messaging.notifications SET status = 'PENDING', locked_at = NULL
WHERE status = 'PROCESSING' AND locked_at <= :stuck_cutoff;

-- name: claim_pending_notifications(now, limit)
SELECT id FROM messaging.notifications
WHERE status = 'PENDING' AND available_at <= :now AND attempts < 5
ORDER BY available_at, id LIMIT :limit
FOR UPDATE SKIP LOCKED;

-- name: update_claimed_notifications(now, notification_ids)!
UPDATE messaging.notifications SET status = 'PROCESSING', locked_at = :now, attempts = attempts + 1
WHERE id = ANY(:notification_ids);

-- name: get_notifications_by_ids(notification_ids)
SELECT id, user_id, subscription_id, notification_type, content, status, available_at, attempts, locked_at, sent_at, last_error, created_at
FROM messaging.notifications WHERE id = ANY(:notification_ids);

-- name: mark_notification_sent(now, notification_id)!
UPDATE messaging.notifications SET status = 'SENT', sent_at = :now, locked_at = NULL WHERE id = :notification_id;

-- name: mark_notification_failed(available_at, error_text, notification_id)!
UPDATE messaging.notifications SET status = 'PENDING', available_at = :available_at, locked_at = NULL, last_error = :error_text
WHERE id = :notification_id;

-- name: insert_notification(id, user_id, subscription_id, notification_type, content, status, available_at, attempts)!
INSERT INTO messaging.notifications (id, user_id, subscription_id, notification_type, content, status, available_at, attempts)
VALUES (:id, :user_id, :subscription_id, :notification_type, :content, :status, :available_at, :attempts);
