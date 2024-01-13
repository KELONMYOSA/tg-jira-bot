import sqlite3

from cryptography.fernet import Fernet

from src.config import settings


class Database:
    __DB_PATH = "src/db/database.sqlite"
    __cipher_suite = Fernet(settings.SECRET_KEY)

    # Устанавливаем соединение с базой данных
    def __init__(self, db_location: str = None):
        if db_location is not None:
            self.connection = sqlite3.connect(db_location)
        else:
            self.connection = sqlite3.connect(self.__DB_PATH)
        self.cur = self.connection.cursor()

    def __enter__(self):
        return self

    # Сохраняем изменения и закрываем соединение
    def __exit__(self, ext_type, exc_value, traceback):
        self.cur.close()
        if isinstance(exc_value, Exception):
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()

    # Проверка авторизации пользователя
    def is_authorized(self, user_id: int) -> bool:
        self.cur.execute("SELECT * FROM user_credentials WHERE tg_user_id = ?", (user_id,))
        user = self.cur.fetchone()
        if user is None:
            return False
        else:
            return True

    # Запись авторизованного пользователя
    def set_user(self, tg_user_id: int, tg_username: str, jira_login: str, jira_password: str):
        encrypted_password = self._encrypt_password(jira_password)
        self.cur.execute(
            "INSERT INTO user_credentials (tg_user_id, tg_username, jira_login, jira_password) VALUES (?, ?, ?, ?)",
            (tg_user_id, tg_username, jira_login, encrypted_password),
        )

    # Получение данных пользователя Jira
    def get_user(self, user_id: int) -> tuple:
        self.cur.execute("SELECT jira_login, jira_password FROM user_credentials WHERE tg_user_id = ?", (user_id,))
        jira_login, jira_password = self.cur.fetchone()
        decrypted_password = self._decrypt_password(jira_password)
        return jira_login, decrypted_password

    # Получение данных Telegram пользователя по данным Jira
    def get_tg_users(self, jira_login: str) -> list:
        self.cur.execute("SELECT tg_user_id, tg_username FROM user_credentials WHERE jira_login = ?", (jira_login,))
        tg_user_data = self.cur.fetchall()
        return tg_user_data

    # Удаление данных пользователя
    def remove_user(self, user_id: int):
        self.cur.execute("DELETE FROM user_credentials WHERE tg_user_id = ?", (user_id,))

    # Шифрование пароля
    def _encrypt_password(self, password: str) -> str:
        return self.__cipher_suite.encrypt(password.encode()).decode()

    # Дешифрование пароля
    def _decrypt_password(self, encrypted_password: str) -> str:
        return self.__cipher_suite.decrypt(encrypted_password).decode()
