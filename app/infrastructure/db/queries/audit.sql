-- name: insert_audit_log(id, actor_user_id, action_code, entity_schema, entity_table, entity_id, old_values, new_values, source, correlation_id)!
INSERT INTO audit.audit_log (id, actor_user_id, action_code, entity_schema, entity_table, entity_id, old_values, new_values, source, correlation_id)
VALUES (:id, :actor_user_id, :action_code, :entity_schema, :entity_table, :entity_id, :old_values::jsonb, :new_values::jsonb, :source, :correlation_id);
