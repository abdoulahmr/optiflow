# models/inventory_model.py
from database.db_manager import db
import random
from datetime import datetime, timedelta

# At the top of the file, after imports
CONTACT_LENS_TYPES = [
    "Lentilles Sphérique (Annuelle)",
    "Lentilles Sphérique (Jetable)",
    "Lentilles Torique (Annuelle)",
    "Lentilles Torique (Jetable)",
    "Lentilles Rigides",
    "Lentilles Thérapeutiques",
    "Lentilles Couleur Esthétique"
]

class InventoryModel:
    @staticmethod
    def generate_barcode():
        """Generates a unique 7-digit barcode starting with 1."""
        while True:
            barcode = f"1{random.randint(100000, 899999)}"
            if not InventoryModel.get_item_by_barcode(barcode):
                return barcode

    @staticmethod
    def get_item_by_barcode(barcode):
        return db.fetch_one("SELECT * FROM inventory WHERE barcode = ?", (barcode,))

    @staticmethod
    def add_item(data):
        data['barcode'] = InventoryModel.generate_barcode()
        data['retail_price'] = data.get('retail_price', 0.0)

        query = """
            INSERT INTO inventory (barcode, name, category, cost_price, retail_price, stock_qty, seuil, expiration_date)
            VALUES (:barcode, :name, :category, :cost_price, :retail_price, :stock_qty, :seuil, :expiration_date)
        """
        return db.execute_query(query, data)
        
    @staticmethod
    def get_all_items(search_term="", category="Tous"):
        query = "SELECT * FROM inventory"
        params = []
        conditions = []
        
        if search_term:
            conditions.append("(name LIKE ? OR barcode LIKE ?)")
            params.extend([f"%{search_term}%"] * 2)
        if category != "Tous":
            conditions.append("category = ?")
            params.append(category)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        query += " ORDER BY name ASC"
        return db.fetch_all(query, tuple(params))

    @staticmethod
    def get_kpis():
        """Calculates dashboard statistics."""
        total_refs = db.fetch_one("SELECT COUNT(*) as count FROM inventory")['count']
        total_value = db.fetch_one("SELECT SUM(cost_price * stock_qty) as total FROM inventory")['total'] or 0.0
        
        low_stock = db.fetch_one("SELECT COUNT(*) as count FROM inventory WHERE stock_qty <= seuil AND stock_qty > 0")['count']
        out_stock = db.fetch_one("SELECT COUNT(*) as count FROM inventory WHERE stock_qty = 0")['count']
        
        # Expiring within 3 months
        three_months_later = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
        expiring = db.fetch_one("SELECT COUNT(*) as count FROM inventory WHERE expiration_date IS NOT NULL AND expiration_date <= ?", (three_months_later,))['count']
        
        return {
            'total_refs': total_refs,
            'total_value': f"{total_value:,.2f} DA",
            'low_stock': low_stock,
            'out_stock': out_stock,
            'expiring': expiring
        }

    @staticmethod
    def get_item_by_id(item_id):
        return db.fetch_one("SELECT * FROM inventory WHERE id = ?", (item_id,))

    @staticmethod
    def restock_item(item_id, quantity_added):
        """Increases stock when buying from a supplier."""
        db.execute_query("UPDATE inventory SET stock_qty = stock_qty + ? WHERE id = ?", (quantity_added, item_id))

    @staticmethod
    def sell_item(item_id, quantity_sold=1):
        """Decreases stock when a sale is finalized in the POS."""
        db.execute_query("UPDATE inventory SET stock_qty = stock_qty - ? WHERE id = ?", (quantity_sold, item_id))

    @staticmethod
    def get_items_by_category(category):
        query = "SELECT * FROM inventory WHERE category = ? ORDER BY name ASC"
        return db.fetch_all(query, (category,))

    @staticmethod
    def update_item(item_id, data):
        query = """
            UPDATE inventory 
            SET name = :name, category = :category, cost_price = :cost_price, 
                retail_price = :retail_price, stock_qty = :stock_qty, seuil = :seuil, expiration_date = :expiration_date
            WHERE id = :id
        """
        data['id'] = item_id
        return db.execute_query(query, data)

    @staticmethod
    def delete_item(item_id):
        db.execute_query("DELETE FROM inventory WHERE id = ?", (item_id,))

    @staticmethod
    def get_all_contact_lenses():
        """Returns all contact lens items across all subtypes."""
        placeholders = ','.join('?' * len(CONTACT_LENS_TYPES))
        query = f"SELECT * FROM inventory WHERE category IN ({placeholders}) ORDER BY name ASC"
        return db.fetch_all(query, tuple(CONTACT_LENS_TYPES))
    
    @staticmethod
    def is_contact_lens(category):
        """Checks if a category is a contact lens type."""
        return category in CONTACT_LENS_TYPES