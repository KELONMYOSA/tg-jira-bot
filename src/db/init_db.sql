CREATE TABLE IF NOT EXISTS user_credentials
(
    tg_user_id    INTEGER PRIMARY KEY,
    tg_username   TEXT,
    jira_login    TEXT NOT NULL,
    jira_password TEXT NOT NULL
);