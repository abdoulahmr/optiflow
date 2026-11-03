# models/auth_model.py
from database.db_manager import db

class AuthModel:
    @staticmethod
    def login(username, password):
        """Checks if credentials are valid. Returns user dict if yes, None if no."""
        return db.fetch_one("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))