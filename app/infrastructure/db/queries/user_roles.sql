-- name: get_user_role(user_id, role_id)^
SELECT user_id, role_id FROM identity.user_roles WHERE user_id = :user_id AND role_id = :role_id;

-- name: get_user_ids_with_role(role_id)
SELECT user_id FROM identity.user_roles WHERE role_id = :role_id;

-- name: insert_user_role(user_id, role_id)!
INSERT INTO identity.user_roles (user_id, role_id) VALUES (:user_id, :role_id);

-- name: delete_user_role(user_id, role_id)!
DELETE FROM identity.user_roles WHERE user_id = :user_id AND role_id = :role_id;
