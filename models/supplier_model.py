# models/supplier_model.py
from database.db_manager import db

class SupplierModel:
    @staticmethod
    def add_supplier(data):
        query = """
            INSERT INTO suppliers (name, contact_person, phone, email, address, category_tag, rc, nif, nis, art, ccp, bank_rib)
            VALUES (:name, :contact_person, :phone, :email, :address, :category_tag, :rc, :nif, :nis, :art, :ccp, :bank_rib)
        """
        return db.execute_query(query, data)

    @staticmethod
    def get_all_suppliers(search_term=""):
        query = "SELECT * FROM suppliers"
        params = {}
        if search_term:
            query += " WHERE name LIKE :search OR phone LIKE :search OR category_tag LIKE :search"
            params['search'] = f"%{search_term}%"
        query += " ORDER BY name ASC"
        return db.fetch_all(query, params)

    @staticmethod
    def get_supplier(supplier_id):
        return db.fetch_one("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))

    @staticmethod
    def add_transaction(supplier_id, trans_type, amount, note=""):
        """Adds an invoice (increases debt) or payment (decreases debt)."""
        query = """
            INSERT INTO supplier_transactions (supplier_id, transaction_type, amount, note)
            VALUES (?, ?, ?, ?)
        """
        db.execute_query(query, (supplier_id, trans_type, amount, note))
        
        # Update live balance
        supplier = SupplierModel.get_supplier(supplier_id)
        current_balance = supplier['balance_due'] if supplier['balance_due'] else 0.0
        
        if trans_type == "Facture":
            current_balance += amount
        elif trans_type == "Versement":
            current_balance -= amount
            
        db.execute_query("UPDATE suppliers SET balance_due = ? WHERE id = ?", (current_balance, supplier_id))

    @staticmethod
    def get_transactions(supplier_id):
        return db.fetch_all("SELECT * FROM supplier_transactions WHERE supplier_id = ? ORDER BY date DESC", (supplier_id,))