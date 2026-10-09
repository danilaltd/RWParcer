-- name: insert_message(id, sender_user_id, receiver_user_id, content)!
INSERT INTO messaging.messages (id, sender_user_id, receiver_user_id, content)
VALUES (:id, :sender_user_id, :receiver_user_id, :content);

-- name: get_user_messages(user_id)
SELECT id, sender_user_id, receiver_user_id, content, sent_at, read_at
FROM messaging.messages WHERE receiver_user_id = :user_id OR sender_user_id = :user_id
ORDER BY sent_at;

-- name: get_all_messages()
SELECT id, sender_user_id, receiver_user_id, content, sent_at, read_at FROM messaging.messages ORDER BY sent_at;
