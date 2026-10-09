-- name: get_role_id(code)$
SELECT id FROM identity.roles WHERE code = :code;

-- name: get_roles()
SELECT id, code, name FROM identity.roles;

-- name: insert_role(id, code, name)!
INSERT INTO identity.roles (id, code, name) VALUES (:id, :code, :name);
