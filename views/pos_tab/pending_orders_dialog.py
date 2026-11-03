# views/pos_tab/pending_orders_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTableView, QHeaderView, QAbstractItemView, 
                               QLineEdit, QMessageBox)
from PySide6.QtCore import Qt, QAbstractTableModel
from PySide6.QtGui import QFont, QColor
from database.db_manager import db
from views.pos_tab.settle_debt_dialog import SettleDebtDialog
from styles import PRIMARY, PRIMARY_HOVER

class PendingOrdersModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self.headers = ["ID", "Date", "Client", "Téléphone", "Ticket", "Total", "Versé", "Reste"]

    def data(self, index, role):
        if role == Qt.DisplayRole:
            row = self._data[index.row()]
            keys = ["id", "created_at", "patient_name", "phone", "client_id_text",
                    "total_payable", "deposit_received", "remaining_balance"]
            value = row[keys[index.column()]]
            if keys[index.column()] == "created_at" and value:
                return str(value)[:10]
            if keys[index.column()] in ["total_payable", "deposit_received", "remaining_balance"]:
                return f"{value:.2f}" if value is not None else "0.00"
            return str(value) if value is not None else ""
        elif role == Qt.ForegroundRole:
            row = self._data[index.row()]
            if index.column() == 7:  # Reste column
                if row['remaining_balance'] > 0:
                    return QColor("#DC2626")
                else:
                    return QColor("#16A34A")
        elif role == Qt.FontRole:
            if index.column() == 7:
                font = QFont()
                font.setBold(True)
                return font
        return None

    def rowCount(self, index): return len(self._data)
    def columnCount(self, index): return len(self.headers)
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

class PendingOrdersDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("💳 Règlement des Dettes (Commandes en Cours)")
        self.resize(1100, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Header
        header = QLabel("Commandes avec Solde Restant à Payer")
        header.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {PRIMARY};")
        layout.addWidget(header)
        
        subtitle = QLabel("Double-cliquez sur une ligne pour enregistrer un paiement")
        subtitle.setStyleSheet("color: #6B7280; font-size: 13px; margin-bottom: 10px;")
        layout.addWidget(subtitle)

        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search")
        self.search_input.setPlaceholderText("Rechercher par client, ticket ou téléphone...")
        self.search_input.textChanged.connect(self.load_data)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Table
        self.table = QTableView()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().stretchLastSection = True
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self.settle_debt)
        layout.addWidget(self.table)

        # Hint
        hint = QLabel("💡 Astuce: Le statut passera automatiquement à 'Livré' une fois le solde réglé")
        hint.setStyleSheet("color: #6B7280; font-size: 12px; font-style: italic;")
        layout.addWidget(hint)

        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Fermer")
        close_btn.setObjectName("primary")
        close_btn.setStyleSheet(f"""
            QPushButton {{ background: {PRIMARY}; color: white; border: none;
                border-radius: 8px; padding: 10px 20px; font-weight: 600; }}
            QPushButton:hover {{ background: {PRIMARY_HOVER}; }}
        """)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        self.load_data()

    def load_data(self):
        search = f"%{self.search_input.text()}%"
        # Query orders with remaining_balance > 0, joined with patient info
        query = """
            SELECT o.id, o.created_at, o.client_id_text,
                   o.total_payable, o.deposit_received, o.remaining_balance, o.status,
                   (p.nom || ' ' || p.prenom) as patient_name,
                   p.phone
            FROM orders o
            LEFT JOIN patients p ON o.patient_id = p.id
            WHERE o.remaining_balance > 0.01
              AND (p.nom LIKE ? OR p.prenom LIKE ? OR o.client_id_text LIKE ? OR p.phone LIKE ?)
            ORDER BY o.created_at DESC
        """
        data = db.fetch_all(query, (search, search, search, search))
        self.model = PendingOrdersModel(data)
        self.table.setModel(self.model)

    def settle_debt(self, index):
        row = index.row()
        order_id = self.model._data[row]["id"]
        
        dialog = SettleDebtDialog(order_id, self)
        if dialog.exec():
            self.load_data()
            # Notify parent to refresh if needed
            if hasattr(self.parent(), 'load_inventory_items'):
                self.parent().load_inventory_items()