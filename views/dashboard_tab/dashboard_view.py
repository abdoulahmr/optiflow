# views/dashboard_tab/dashboard_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFrame, QGridLayout)
from PySide6.QtCore import Qt
from styles import StatCard
from database.db_manager import db

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Tableau de bord")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Vue d'ensemble de l'activité de l'optique")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        kpi_layout = QGridLayout()
        kpi_layout.setSpacing(15)

        self.card_patients = StatCard("Total Clients", "0", "Patients enregistrés", "#2563EB")
        self.card_items = StatCard("Articles en Stock", "0", "Montures, Lentilles, etc.", "#16A34A")
        self.card_stock_value = StatCard("Valeur du Stock", "0 DA", "Valeur d'achat totale (Inv + Verres)", "#D97706")
        self.card_pending = StatCard("Commandes En Cours", "0", "Ordonnances à finaliser", "#DC2626")
        self.card_suppliers = StatCard("Fournisseurs", "0", "Partenaires actifs", "#2563EB")
        self.card_debt = StatCard("Dette Fournisseurs", "0 DA", "Solde global dû", "#DC2626")

        kpi_layout.addWidget(self.card_patients, 0, 0)
        kpi_layout.addWidget(self.card_items, 0, 1)
        kpi_layout.addWidget(self.card_stock_value, 0, 2)
        kpi_layout.addWidget(self.card_pending, 1, 0)
        kpi_layout.addWidget(self.card_suppliers, 1, 1)
        kpi_layout.addWidget(self.card_debt, 1, 2)
        
        layout.addLayout(kpi_layout)
        layout.addStretch()
        
        self.load_data()

    def load_data(self):
        total_patients = db.fetch_one("SELECT COUNT(*) as count FROM patients")['count']
        total_suppliers = db.fetch_one("SELECT COUNT(*) as count FROM suppliers")['count']
        
        pending_orders = db.fetch_one("SELECT COUNT(*) as count FROM orders WHERE status = 'En cours'")['count']
        total_debt = db.fetch_one("SELECT SUM(balance_due) as total FROM suppliers")['total'] or 0.0

        # Combined Stock Value (Inventory + Lenses)
        inv_stats = db.fetch_one("SELECT COUNT(*) as count, COALESCE(SUM(cost_price * stock_qty), 0) as value FROM inventory")
        lens_stats = db.fetch_one("SELECT COALESCE(SUM(cost_price * stock_qty), 0) as value FROM lenses")
        
        total_items = inv_stats['count'] if inv_stats['count'] else 0
        stock_value = (inv_stats['value'] if inv_stats['value'] else 0) + (lens_stats['value'] if lens_stats['value'] else 0)

        self.card_patients.value_label.setText(str(total_patients))
        self.card_items.value_label.setText(str(total_items))
        self.card_stock_value.value_label.setText(f"{stock_value:,.0f} DA")
        self.card_pending.value_label.setText(str(pending_orders))
        self.card_suppliers.value_label.setText(str(total_suppliers))
        self.card_debt.value_label.setText(f"{total_debt:,.0f} DA")