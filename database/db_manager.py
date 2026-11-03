# database/db_manager.py
import sqlite3
import os
from config import DB_PATH, BASE_DIR

class DBManager:
    def __init__(self):
        self.conn = None
        self.connect()
        self.initialize_schema()

    def connect(self):
        try:
            self.conn = sqlite3.connect(DB_PATH)
            self.conn.row_factory = sqlite3.Row 
            self.conn.execute("PRAGMA foreign_keys = ON;")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def initialize_schema(self):
        # Look for schema.sql in BASE_DIR (PyInstaller _internal folder)
        schema_path = os.path.join(BASE_DIR, "database", "schema.sql")
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_script = f.read()
            cursor = self.conn.cursor()
            cursor.executescript(schema_script)
            self.conn.commit()
        except Exception as e:
            print(f"Error initializing schema: {e}")

    def execute_query(self, query, params=()):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Query Error: {e}")
            return None

    def fetch_all(self, query, params=()):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Fetch All Error: {e}")
            return []

    def fetch_one(self, query, params=()):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Fetch One Error: {e}")
            return None

# Create a global instance to use across the app
db = DBManager()