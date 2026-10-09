-- name: insert_availability_snapshot(id, subscription_id, checked_at)!
INSERT INTO monitoring.availability_snapshots (id, subscription_id, checked_at)
VALUES (:id, :subscription_id, :checked_at);

-- name: get_latest_snapshot(subscription_id)^
SELECT id, subscription_id, checked_at, created_at FROM monitoring.availability_snapshots
WHERE subscription_id = :subscription_id ORDER BY checked_at DESC LIMIT 1;

-- name: get_snapshot_seats(snapshot_id)
SELECT snapshot_id, unit_type, unit_number, place_code FROM monitoring.availability_snapshot_seats
WHERE snapshot_id = :snapshot_id;

-- name: insert_snapshot_seat(snapshot_id, unit_type, unit_number, place_code)!
INSERT INTO monitoring.availability_snapshot_seats (snapshot_id, unit_type, unit_number, place_code)
VALUES (:snapshot_id, :unit_type, :unit_number, :place_code);
