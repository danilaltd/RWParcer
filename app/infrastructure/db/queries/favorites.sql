-- name: get_favorites_for_user(user_id)
SELECT id, user_id, service_route_id, created_at FROM monitoring.favorites WHERE user_id = :user_id;

-- name: favorite_exists(user_id, service_route_id)$
SELECT (COUNT(*) > 0) AS exists FROM monitoring.favorites WHERE user_id = :user_id AND service_route_id = :service_route_id;

-- name: insert_favorite(id, user_id, service_route_id)!
INSERT INTO monitoring.favorites (id, user_id, service_route_id) VALUES (:id, :user_id, :service_route_id);

-- name: delete_favorite(favorite_id)!
DELETE FROM monitoring.favorites WHERE id = :favorite_id;
