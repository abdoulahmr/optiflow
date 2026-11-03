# models/charge_model.py
from database.db_manager import db

class ChargeModel:
    @staticmethod
    def add_charge(data):
        query = "INSERT INTO charges (description, category, amount) VALUES (?, ?, ?)"
        return db.execute_query(query, (data['description'], data['category'], data['amount']))
        
    @staticmethod
    def get_total_charges():
        res = db.fetch_one("SELECT COALESCE(SUM(amount), 0) as total FROM charges")
        return res['total'] if res else 0.0

    @staticmethod
    def get_all_charges(search_term="", start_date=None, end_date=None):
        query = "SELECT id, date, description, category, amount FROM charges"
        params = []
        conditions = []
        
        if search_term:
            conditions.append("(description LIKE ? OR category LIKE ?)")
            params.extend([f"%{search_term}%", f"%{search_term}%"])
            
        if start_date:
            conditions.append("date(date) >= date(?)")
            params.append(start_date)
            
        if end_date:
            conditions.append("date(date) <= date(?)")
            params.append(end_date)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        query += " ORDER BY date DESC"
        return db.fetch_all(query, tuple(params))