BEGIN TRANSACTION;

CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    is_bot BOOLEAN NOT NULL DEFAULT FALSE,
    first_name TEXT NOT NULL,
    last_name TEXT DEFAULT NULL,
    username TEXT DEFAULT NULL,
    language_code TEXT DEFAULT NULL,
    is_premium BOOLEAN DEFAULT NULL,
    added_to_attachment_menu BOOLEAN DEFAULT NULL,
    can_join_groups BOOLEAN DEFAULT NULL,
    can_read_all_group_messages BOOLEAN DEFAULT NULL,
    supports_guest_queries BOOLEAN DEFAULT NULL,
    supports_inline_queries BOOLEAN DEFAULT NULL,
    can_connect_to_business BOOLEAN DEFAULT NULL,
    has_main_web_app BOOLEAN DEFAULT NULL,
    has_topics_enabled BOOLEAN DEFAULT NULL,
    allows_users_to_create_topics BOOLEAN DEFAULT NULL,
    can_manage_bots BOOLEAN DEFAULT NULL,

    zoneinfo TEXT DEFAULT NULL,
    date_db TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(username)
);

CREATE TABLE chats (
    id BIGINT PRIMARY KEY,
    "type" TEXT NOT NULL,
    title TEXT DEFAULT NULL,
    username TEXT DEFAULT NULL,
    first_name TEXT DEFAULT NULL,
    last_name TEXT DEFAULT NULL,
    is_forum BOOLEAN DEFAULT NULL,
    is_direct_messages BOOLEAN DEFAULT NULL,
    language_code TEXT DEFAULT NULL,

    owner_id BIGINT REFERENCES users(id) ON DELETE SET NULL DEFAULT NULL,
    zoneinfo TEXT DEFAULT NULL,    
    date_db TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(username)
);

-- CREATE TABLE messages (
--     message_id INTEGER NOT NULL,
--     "date" TIMESTAMP NOT NULL,
--     chat BIGINT REFERENCES chats(id) NOT NULL,
--     message_thread_id INTEGER DEFAULT NULL,
--     from_user BIGINT REFERENCES users(id) DEFAULT NULL,
--     reply_to_message INTEGER REFERENCES messages(message_id) DEFAULT NULL,
--     quote TEXT DEFAULT NULL,
--     paid_star_count INTEGER DEFAULT NULL,
--     "text" TEXT DEFAULT NULL,
--     caption TEXT DEFAULT NULL
-- );

CREATE TABLE api_keys (
    api_key TEXT PRIMARY KEY,
    permissions VARCHAR(4) NOT NULL DEFAULT 'r',
    is_superkey BOOLEAN NOT NULL DEFAULT FALSE,
    owner_id BIGINT REFERENCES users(id) ON DELETE CASCADE DEFAULT NULL,
    date_db TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(owner_id)
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_chats_username ON chats(username);
CREATE INDEX idx_chats_owner_id ON chats(owner_id);
CREATE INDEX idx_api_keys_owner_id ON api_keys(owner_id);

COMMIT;