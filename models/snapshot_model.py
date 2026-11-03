# models/snapshot_model.py
from database.db_manager import db
from models.finance_model import FinanceModel

class SnapshotModel:
    @staticmethod
    def save_snapshot(period_type, period_value):
        """Fetches live KPIs and saves them as a frozen snapshot."""
        kpis = FinanceModel.get_kpis()
        
        query = """
            INSERT OR REPLACE INTO financial_snapshots 
            (period_type, period_value, revenue, realized_profit, total_charges, net_profit, stock_value, total_debt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return db.execute_query(query, (
            period_type, period_value,
            kpis['total_revenue'], kpis['realized_profit'], kpis['total_charges'],
            kpis['net_profit'], kpis['total_stock_value'], kpis['total_debt']
        ))

    @staticmethod
    def get_all_snapshots():
        return db.fetch_all("SELECT * FROM financial_snapshots ORDER BY date_saved DESC")