# models/finance_model.py
from database.db_manager import db

class FinanceModel:
    @staticmethod
    def get_kpis():
        from models.lens_stock_model import LensStockModel
        
        sales = db.fetch_one("SELECT COALESCE(SUM(total_payable), 0) as total FROM orders")
        total_revenue = sales['total'] if sales else 0.0
        
        debt = db.fetch_one("SELECT COALESCE(SUM(balance_due), 0) as total FROM suppliers")
        total_debt = debt['total'] if debt else 0.0
        
        # Inventory stock value
        inv_stats = db.fetch_one("SELECT COALESCE(SUM(cost_price * stock_qty), 0) as cost, COALESCE(SUM((retail_price - cost_price) * stock_qty), 0) as profit FROM inventory")
        
        # Lens stock value (from new entries table)
        lens_stock_value = LensStockModel.get_total_stock_value()
        
        # Potential profit for lenses: (retail - cost) * total_stock_qty_per_lens
        # We need to sum across all entries
        lens_profit_res = db.fetch_one("""
            SELECT COALESCE(SUM(lse.quantity * (l.retail_price - l.cost_price)), 0) as profit
            FROM lens_stock_entries lse
            JOIN lenses l ON lse.lens_id = l.id
        """)
        lens_potential_profit = lens_profit_res['profit'] if lens_profit_res else 0.0
        
        total_stock_value = (inv_stats['cost'] if inv_stats else 0) + lens_stock_value
        total_potential_profit = (inv_stats['profit'] if inv_stats else 0) + lens_potential_profit
        
        profit_query = db.fetch_one("SELECT COALESCE(SUM(price - discount - cost_price), 0) as profit FROM order_items")
        realized_profit = profit_query['profit'] if profit_query else 0.0
        
        from models.charge_model import ChargeModel
        total_charges = ChargeModel.get_total_charges()
        net_profit = realized_profit - total_charges
        
        return {
            'total_revenue': total_revenue,
            'total_debt': total_debt,
            'total_stock_value': total_stock_value,
            'total_potential_profit': total_potential_profit,
            'realized_profit': realized_profit,
            'total_charges': total_charges,
            'net_profit': net_profit
        }

    @staticmethod
    def get_sales_history(search_term="", status="Tous", start_date=None, end_date=None):
        query = """
            SELECT o.id, o.created_at, p.nom || ' ' || p.prenom as patient_name, o.client_id_text, 
                   o.total_payable, o.deposit_received, o.remaining_balance, o.status
            FROM orders o
            LEFT JOIN patients p ON o.patient_id = p.id
        """
        params = []
        conditions = []
        
        if search_term:
            conditions.append("(p.nom LIKE ? OR p.prenom LIKE ? OR o.client_id_text LIKE ?)")
            params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])
            
        if status != "Tous":
            conditions.append("o.status = ?")
            params.append(status)
            
        if start_date:
            conditions.append("date(o.created_at) >= date(?)")
            params.append(start_date)
            
        if end_date:
            conditions.append("date(o.created_at) <= date(?)")
            params.append(end_date)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        query += " ORDER BY o.created_at DESC"
        return db.fetch_all(query, tuple(params))

    @staticmethod
    def get_order_items(order_id):
        query = """
            SELECT item_type, description, price, discount 
            FROM order_items 
            WHERE order_id = ?
        """
        return db.fetch_all(query, (order_id,))