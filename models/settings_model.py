# models/settings_model.py
from database.db_manager import db
import os
import shutil
from datetime import datetime
from config import DB_PATH, BASE_DIR

class SettingsModel:
    @staticmethod
    def get_setting(key):
        result = db.fetch_one("SELECT value FROM settings WHERE key = ?", (key,))
        return result['value'] if result else None

    @staticmethod
    def update_setting(key, value):
        db.execute_query("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))

    @staticmethod
    def get_all_users():
        return db.fetch_all("SELECT id, username, role FROM users ORDER BY username ASC")

    @staticmethod
    def add_user(username, password, role):
        return db.execute_query("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))

    @staticmethod
    def delete_user(user_id):
        db.execute_query("DELETE FROM users WHERE id = ?", (user_id,))

    @staticmethod
    def backup_database():
        """Creates a timestamped copy of the SQLite database."""
        from config import DATA_DIR
        backup_dir = os.path.join(DATA_DIR, "backups")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"optiflow_backup_{timestamp}.db")
        
        try:
            shutil.copy2(DB_PATH, backup_path)
            return backup_path
        except Exception as e:
            print(f"Backup error: {e}")
            return None
            
    @staticmethod
    def get_license_key():
        return SettingsModel.get_setting('license_key')

    @staticmethod
    def set_license_key(key):
        SettingsModel.update_setting('license_key', key)

    @staticmethod
    def is_app_activated():
        val = SettingsModel.get_setting('is_activated')
        return val == 'True'

    @staticmethod
    def update_password(user_id, new_password):
        db.execute_query("UPDATE users SET password = ? WHERE id = ?", (new_password, user_id))

    @staticmethod
    def has_users():
        """Checks if any users exist in the database (for first-time setup)."""
        result = db.fetch_one("SELECT COUNT(*) as count FROM users")
        return result['count'] > 0 if result else False

    @staticmethod
    def export_to_excel(file_path):
        """Exports all database tables to an Excel file with multiple sheets."""
        import pandas as pd
        
        tables = {
            'Patients': 'SELECT * FROM patients ORDER BY nom',
            'Prescriptions': 'SELECT * FROM prescriptions ORDER BY exam_date DESC',
            'Contact_Lenses': 'SELECT * FROM contact_lenses ORDER BY fitting_date DESC',
            'Lenses_Matrix': 'SELECT * FROM lenses ORDER BY type, optical_group, treatment',
            'Lens_Stock': 'SELECT * FROM lens_stock_entries ORDER BY lens_id',
            'Inventory': 'SELECT * FROM inventory ORDER BY category, name',
            'Suppliers': 'SELECT * FROM suppliers ORDER BY name',
            'Supplier_Transactions': 'SELECT * FROM supplier_transactions ORDER BY date DESC',
            'Orders': 'SELECT * FROM orders ORDER BY created_at DESC',
            'Order_Items': 'SELECT * FROM order_items ORDER BY order_id',
            'Charges': 'SELECT * FROM charges ORDER BY date DESC',
            'Snapshots': 'SELECT * FROM financial_snapshots ORDER BY date_saved DESC',
            'Users': 'SELECT id, username, role FROM users ORDER BY username',
            'Settings': 'SELECT * FROM settings'
        }
        
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                for sheet_name, query in tables.items():
                    data = db.fetch_all(query)
                    if data:
                        df = pd.DataFrame([dict(row) for row in data])
                    else:
                        df = pd.DataFrame()
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            return True
        except Exception as e:
            print(f"Excel export error: {e}")
            return False
    
    @staticmethod
    def verify_password(password):
        """Verifies if the given password matches any admin user."""
        admin = db.fetch_one(
            "SELECT id FROM users WHERE role='Administrateur' AND password=?",
            (password,)
        )
        return admin is not None
    
    @staticmethod
    def delete_all_data():
        """Deletes all transactional data but keeps users and settings."""
        tables = [
            'order_items', 'orders', 'supplier_transactions', 'charges',
            'financial_snapshots', 'contact_lenses', 'prescriptions',
            'patients', 'lens_stock_entries', 'inventory'
        ]
        
        db.execute_query("PRAGMA foreign_keys = OFF;")
        for table in tables:
            db.execute_query(f"DELETE FROM {table};")
            db.execute_query(f"DELETE FROM sqlite_sequence WHERE name='{table}';")
        
        # Reset lens prices and stock to 0 (keep structure)
        db.execute_query("UPDATE lenses SET retail_price=0, cost_price=0, stock_qty=0;")
        
        # Reset supplier balances
        db.execute_query("UPDATE suppliers SET balance_due=0;")
        
        db.execute_query("PRAGMA foreign_keys = ON;")
        return True
    
    @staticmethod
    def reset_database():
        """Completely resets the database - deletes ALL data including users."""
        tables = [
            'order_items', 'orders', 'supplier_transactions', 'charges',
            'financial_snapshots', 'contact_lenses', 'prescriptions',
            'patients', 'lens_stock_entries', 'inventory', 'lenses',
            'suppliers', 'users', 'settings'
        ]
        
        db.execute_query("PRAGMA foreign_keys = OFF;")
        for table in tables:
            db.execute_query(f"DELETE FROM {table};")
            db.execute_query(f"DELETE FROM sqlite_sequence WHERE name='{table}';")
        db.execute_query("PRAGMA foreign_keys = ON;")
        return True

    @staticmethod
    def backup_database_to_path(target_path):
        """Creates a backup of the SQLite database at the specified path."""
        import shutil
        from config import DB_PATH
        
        try:
            shutil.copy2(DB_PATH, target_path)
            return target_path
        except Exception as e:
            print(f"Backup error: {e}")
            return None

    @staticmethod
    def get_trial_start_date():
        """Returns the trial start date string (YYYY-MM-DD) or None."""
        return SettingsModel.get_setting('trial_start_date')
    
    @staticmethod
    def start_trial():
        """Records the trial start date as today."""
        from datetime import date
        today = date.today().isoformat()
        SettingsModel.update_setting('trial_start_date', today)
        SettingsModel.update_setting('trial_used', 'True')
    
    @staticmethod
    def get_trial_days_remaining():
        """Returns days remaining in trial. 0 if expired or not started."""
        from datetime import date, datetime
        start_str = SettingsModel.get_trial_start_date()
        if not start_str:
            return 0
        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
            today = date.today()
            elapsed = (today - start_date).days
            remaining = 7 - elapsed
            return max(0, remaining)
        except Exception:
            return 0
    
    @staticmethod
    def is_trial_active():
        """Returns True if trial is within 7 days."""
        return SettingsModel.get_trial_days_remaining() > 0
    
    @staticmethod
    def is_trial_used():
        """Returns True if trial has been started (even if expired)."""
        val = SettingsModel.get_setting('trial_used')
        return val == 'True'