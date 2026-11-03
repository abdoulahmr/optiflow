# views/suppliers_tab/suppliers_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QTableView, QHeaderView)
from PySide6.QtCore import Qt, QAbstractTableModel
from models.supplier_model import SupplierModel
from views.suppliers_tab.supplier_dialog import SupplierDialog
from views.suppliers_tab.supplier_ledger_dialog import SupplierLedgerDialog

class SupplierTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self.headers = ["ID", "Nom", "Catégorie", "Téléphone", "Solde Dû"]

    def data(self, index, role):
        if role == Qt.DisplayRole:
            row = self._data[index.row()]
            keys = ["id", "name", "category_tag", "phone", "balance_due"]
            value = row[keys[index.column()]]
            if keys[index.column()] == "balance_due":
                return f"{value:.2f} DA" if value else "0.00 DA"
            return str(value) if value else ""
        elif role == Qt.ForegroundRole:
            row = self._data[index.row()]
            if row['balance_due'] and row['balance_due'] > 0 and index.column() == 4:
                return Qt.red
        return None

    def rowCount(self, index): return len(self._data)
    def columnCount(self, index): return len(self.headers)
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal: return self.headers[section]
        return None

class SuppliersView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # 1. Header
        title = QLabel("Fournisseurs")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Gérez les profils et la comptabilité fournisseurs")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        # 2. Action Bar
        action_bar = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search")
        self.search_input.setPlaceholderText("Rechercher un fournisseur...")
        self.search_input.textChanged.connect(self.load_suppliers)
        
        self.add_btn = QPushButton("＋ Ajouter Fournisseur")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background: #2563EB;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #1D4ED8;
            }
        """)
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.clicked.connect(self.open_add_dialog)
        
        action_bar.addWidget(self.search_input)
        action_bar.addWidget(self.add_btn)
        layout.addLayout(action_bar)

        # 3. Table
        self.table = QTableView()
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setEditTriggers(QTableView.NoEditTriggers)
        self.table.horizontalHeader().stretchLastSection = True
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self.open_ledger_dialog)
        layout.addWidget(self.table)

        self.load_suppliers()

    def load_suppliers(self):
        search = self.search_input.text()
        suppliers = SupplierModel.get_all_suppliers(search)
        self.model = SupplierTableModel(suppliers)
        self.table.setModel(self.model)

    def open_add_dialog(self):
        dialog = SupplierDialog(self)
        if dialog.exec():
            self.load_suppliers()

    def open_ledger_dialog(self, index):
        row = index.row()
        supplier_id = self.model._data[row]["id"]
        dialog = SupplierLedgerDialog(supplier_id, self)
        dialog.exec()
        self.load_suppliers() # Refresh list to update balance shown in table