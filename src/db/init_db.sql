CREATE TABLE IF NOT EXISTS user_credentials
(
    tg_user_id    INTEGER PRIMARY KEY,
    tg_username   TEXT,
    jira_login    TEXT NOT NULL,
    jira_password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_registration
(
    tg_user_id    INTEGER PRIMARY KEY,
    tg_username   TEXT,
    jira_login    TEXT NOT NULL,
    UNIQUE(tg_username, jira_login)
);