# models/pos_model.py
from database.db_manager import db
import random
from models.inventory_model import InventoryModel 
from models.lens_model import LensModel           

class POSModel:
    @staticmethod
    def generate_client_id():
        """Generates a unique short ID for the receipt (e.g., ORD-8374)"""
        return f"ORD-{random.randint(1000, 9999)}"

    @staticmethod
    def create_order(patient_id, items, deposit, payment_method, status="En cours"):
        from models.lens_stock_model import LensStockModel
        
        client_id_text = POSModel.generate_client_id()
        total_payable = sum(item['price'] - item.get('discount', 0) for item in items)
        remaining_balance = total_payable - deposit
        
        order_query = """
            INSERT INTO orders (patient_id, client_id_text, total_payable, deposit_received, remaining_balance, status, payment_method)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        order_id = db.execute_query(order_query, (
            patient_id, client_id_text, total_payable, deposit, remaining_balance, status, payment_method
        ))
        
        if order_id:
            for item in items:
                # Fetch cost price
                cost = 0.0
                if 'inventory_id' in item:
                    inv = InventoryModel.get_item_by_id(item['inventory_id'])
                    if inv: cost = inv['cost_price']
                elif 'lens_id' in item:
                    lens = db.fetch_one("SELECT cost_price FROM lenses WHERE id=?", (item['lens_id'],))
                    if lens: cost = lens['cost_price']
                
                item_query = """
                    INSERT INTO order_items (order_id, item_type, description, price, discount, cost_price)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                db.execute_query(item_query, (
                    order_id, item['type'], item['description'], item['price'], 
                    item.get('discount', 0), cost
                ))
                
                # Decrement Lens Stock (specific SPH/CYL combo)
                if 'lens_id' in item and item['lens_id']:
                    LensStockModel.sell_entry(
                        item['lens_id'], 
                        item['sph'], 
                        item['cyl'], 
                        1
                    )
                
                # Decrement Inventory Stock (Frames, Solutions, etc.)
                if 'inventory_id' in item and item['inventory_id']:
                    InventoryModel.sell_item(item['inventory_id'], 1)
                    
        return order_id, client_id_text

    @staticmethod
    def add_payment(order_id, amount, payment_method):
        """Adds a new payment to an existing order (for settling debts)."""
        order = db.fetch_one("SELECT total_payable, deposit_received, remaining_balance, status FROM orders WHERE id=?", (order_id,))
        if not order:
            return False
        
        new_deposit = order['deposit_received'] + amount
        new_balance = order['total_payable'] - new_deposit
        
        # If fully paid, mark as delivered
        if new_balance <= 0.01:
            new_status = "Livré"
            new_balance = 0.0
        else:
            new_status = "En cours"
        
        db.execute_query(
            "UPDATE orders SET deposit_received=?, remaining_balance=?, status=? WHERE id=?",
            (new_deposit, new_balance, new_status, order_id)
        )
        
        # Record the payment as a transaction (for history)
        db.execute_query(
            "INSERT INTO order_items (order_id, item_type, description, price, discount, cost_price) VALUES (?, ?, ?, ?, ?, ?)",
            (order_id, "Paiement", f"Versement ({payment_method})", -amount, 0, 0)
        )
        
        return True