# models/lens_stock_model.py
from database.db_manager import db

class LensStockModel:
    @staticmethod
    def get_entries(lens_id):
        """Returns all stock entries for a specific lens (group+treatment+type)."""
        return db.fetch_all(
            "SELECT id, sph, cyl, quantity FROM lens_stock_entries WHERE lens_id = ? ORDER BY sph, cyl",
            (lens_id,)
        )
    
    @staticmethod
    def get_total_stock(lens_id):
        """Returns sum of all quantities for a lens."""
        res = db.fetch_one(
            "SELECT COALESCE(SUM(quantity), 0) as total FROM lens_stock_entries WHERE lens_id = ?",
            (lens_id,)
        )
        return res['total'] if res else 0
    
    @staticmethod
    def add_entry(lens_id, sph, cyl, quantity):
        """Adds a new stock entry, or updates quantity if SPH/CYL combo already exists."""
        existing = db.fetch_one(
            "SELECT id, quantity FROM lens_stock_entries WHERE lens_id=? AND sph=? AND cyl=?",
            (lens_id, sph, cyl)
        )
        if existing:
            new_qty = existing['quantity'] + quantity
            db.execute_query(
                "UPDATE lens_stock_entries SET quantity=? WHERE id=?",
                (new_qty, existing['id'])
            )
            return existing['id']
        else:
            return db.execute_query(
                "INSERT INTO lens_stock_entries (lens_id, sph, cyl, quantity) VALUES (?, ?, ?, ?)",
                (lens_id, sph, cyl, quantity)
            )
    
    @staticmethod
    def update_quantity(entry_id, quantity):
        """Sets the absolute quantity for an existing entry."""
        db.execute_query(
            "UPDATE lens_stock_entries SET quantity=? WHERE id=?",
            (quantity, entry_id)
        )
    
    @staticmethod
    def delete_entry(entry_id):
        db.execute_query("DELETE FROM lens_stock_entries WHERE id=?", (entry_id,))
    
    @staticmethod
    def get_stock_for_combo(lens_id, sph, cyl):
        """Returns quantity available for a specific lens + SPH + CYL combination."""
        res = db.fetch_one(
            "SELECT quantity FROM lens_stock_entries WHERE lens_id=? AND sph=? AND cyl=?",
            (lens_id, sph, cyl)
        )
        return res['quantity'] if res else 0
    
    @staticmethod
    def sell_entry(lens_id, sph, cyl, qty_sold=1):
        """Decrements stock for a specific SPH/CYL combo during a sale."""
        entry = db.fetch_one(
            "SELECT id, quantity FROM lens_stock_entries WHERE lens_id=? AND sph=? AND cyl=?",
            (lens_id, sph, cyl)
        )
        if entry:
            new_qty = max(0, entry['quantity'] - qty_sold)
            db.execute_query(
                "UPDATE lens_stock_entries SET quantity=? WHERE id=?",
                (new_qty, entry['id'])
            )
            return True
        return False
    
    @staticmethod
    def get_total_stock_value():
        """Returns total stock value (cost) across all lenses."""
        res = db.fetch_one("""
            SELECT COALESCE(SUM(lse.quantity * l.cost_price), 0) as value
            FROM lens_stock_entries lse
            JOIN lenses l ON lse.lens_id = l.id
        """)
        return res['value'] if res else 0.0
    
    @staticmethod
    def get_total_stock_count():
        """Returns total number of physical lens pieces in stock."""
        res = db.fetch_one("SELECT COALESCE(SUM(quantity), 0) as total FROM lens_stock_entries")
        return res['total'] if res else 0