# views/finance_tab/finance_view.py
from views.finance_tab.sales_history_dialog import SalesHistoryDialog
from views.finance_tab.charge_dialog import ChargeDialog
from views.finance_tab.expenses_history_dialog import ExpensesHistoryDialog
from views.finance_tab.snapshot_dialog import SnapshotDialog
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel, 
                               QPushButton, QHBoxLayout) 
from PySide6.QtCore import Qt
from styles import StatCard, PRIMARY, PRIMARY_HOVER, TEXT, BORDER
from models.finance_model import FinanceModel
from models.charge_model import ChargeModel

class FinanceView(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(12)

        # 1. Header
        title = QLabel("Finance & Trésorerie")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Vue d'ensemble des ventes, des dettes, des dépenses et de la rentabilité")
        subtitle.setObjectName("pageSubtitle")
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # 2. Action Bar
        action_bar = QHBoxLayout()
        action_bar.addStretch()
        
        snapshots_btn = QPushButton("Clôtures")
        snapshots_btn.setStyleSheet(f"QPushButton {{ background: {PRIMARY}; color: white; border: none; border-radius: 8px; padding: 10px 16px; font-weight: 600; }} QPushButton:hover {{ background: {PRIMARY_HOVER}; }}")
        snapshots_btn.setCursor(Qt.PointingHandCursor)
        snapshots_btn.clicked.connect(self.open_snapshots)
        
        full_history_btn = QPushButton("Voir Ventes")
        full_history_btn.setStyleSheet(f"QPushButton {{ background: {PRIMARY}; color: white; border: none; border-radius: 8px; padding: 10px 16px; font-weight: 600; }} QPushButton:hover {{ background: {PRIMARY_HOVER}; }}")
        full_history_btn.setCursor(Qt.PointingHandCursor)
        full_history_btn.clicked.connect(self.open_full_history)
        
        expenses_history_btn = QPushButton("Voir Dépenses")
        expenses_history_btn.setStyleSheet(f"QPushButton {{ background: {PRIMARY}; color: white; border: none; border-radius: 8px; padding: 10px 16px; font-weight: 600; }} QPushButton:hover {{ background: {PRIMARY_HOVER}; }}")
        expenses_history_btn.setCursor(Qt.PointingHandCursor)
        expenses_history_btn.clicked.connect(self.open_expenses_history)
        
        add_charge_btn = QPushButton("＋ Ajouter Dépense")
        add_charge_btn.setStyleSheet(f"QPushButton {{ background: {PRIMARY}; color: white; border: none; border-radius: 8px; padding: 10px 16px; font-weight: 600; }} QPushButton:hover {{ background: {PRIMARY_HOVER}; }}")
        add_charge_btn.setCursor(Qt.PointingHandCursor)
        add_charge_btn.clicked.connect(self.open_charge_dialog)
        
        action_bar.addWidget(snapshots_btn)
        action_bar.addWidget(full_history_btn)
        action_bar.addWidget(expenses_history_btn)
        action_bar.addWidget(add_charge_btn)
        main_layout.addLayout(action_bar)

        # 3. KPI Grid (6 Cards)
        kpi_layout = QGridLayout()
        kpi_layout.setSpacing(10)

        self.card_revenue = StatCard("Chiffre d'Affaires", "0 DA", "Total des ventes", "#2563EB")
        self.card_real_profit = StatCard("Profit Réalisé", "0 DA", "Bénéfice sur ventes", "#0D9488")
        self.card_charges = StatCard("Dépenses Totales", "0 DA", "Charges d'exploitation", "#D97706")
        self.card_net = StatCard("Profit Net", "0 DA", "Profit Réalisé - Dépenses", "#16A34A")
        self.card_debt = StatCard("Dettes Fournisseurs", "0 DA", "Solde global dû", "#DC2626")
        self.card_stock = StatCard("Valeur du Stock", "0 DA", "Capital immobilisé", "#6B7280")

        kpi_layout.addWidget(self.card_revenue, 0, 0)
        kpi_layout.addWidget(self.card_real_profit, 0, 1)
        kpi_layout.addWidget(self.card_charges, 0, 2)
        kpi_layout.addWidget(self.card_net, 1, 0)
        kpi_layout.addWidget(self.card_debt, 1, 1)
        kpi_layout.addWidget(self.card_stock, 1, 2)
        
        main_layout.addLayout(kpi_layout)
        main_layout.addStretch()

        self.load_data()

    def load_data(self):
        kpis = FinanceModel.get_kpis()
        self.card_revenue.value_label.setText(f"{kpis['total_revenue']:,.0f} DA")
        self.card_real_profit.value_label.setText(f"{kpis['realized_profit']:,.0f} DA")
        self.card_charges.value_label.setText(f"{kpis['total_charges']:,.0f} DA")
        self.card_net.value_label.setText(f"{kpis['net_profit']:,.0f} DA")
        self.card_debt.value_label.setText(f"{kpis['total_debt']:,.0f} DA")
        self.card_stock.value_label.setText(f"{kpis['total_stock_value']:,.0f} DA")
        
    def open_full_history(self):
        SalesHistoryDialog(self).exec()

    def open_charge_dialog(self):
        if ChargeDialog(self).exec():
            self.load_data()

    def open_expenses_history(self):
        ExpensesHistoryDialog(self).exec()
        
    def open_snapshots(self):
        SnapshotDialog(self).exec()