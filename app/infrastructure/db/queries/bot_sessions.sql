-- name: get_conversation_session(user_id)^
SELECT user_id, current_command_code, last_input_date, init_state, context, expires_at, updated_at
FROM bot.conversation_sessions WHERE user_id = :user_id;

-- name: insert_conversation_session(user_id, current_command_code, last_input_date, init_state, context, expires_at)!
INSERT INTO bot.conversation_sessions (user_id, current_command_code, last_input_date, init_state, context, expires_at)
VALUES (:user_id, :current_command_code, :last_input_date, :init_state, :context::jsonb, :expires_at);

-- name: update_conversation_session(current_command_code, last_input_date, init_state, context, expires_at, user_id)!
UPDATE bot.conversation_sessions SET current_command_code = :current_command_code, last_input_date = :last_input_date, init_state = :init_state, context = :context::jsonb, expires_at = :expires_at
WHERE user_id = :user_id;

-- name: delete_conversation_session(user_id)!
DELETE FROM bot.conversation_sessions WHERE user_id = :user_id;
