# views/suppliers_tab/supplier_ledger_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QTableView, QHeaderView, QDoubleSpinBox, QComboBox, 
                               QLineEdit, QGroupBox, QFormLayout, QMessageBox)
from PySide6.QtCore import Qt, QAbstractTableModel
from models.supplier_model import SupplierModel

class TransactionTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self.headers = ["Date", "Type", "Montant", "Note"]

    def data(self, index, role):
        if role == Qt.DisplayRole:
            row = self._data[index.row()]
            keys = ["date", "transaction_type", "amount", "note"]
            value = row[keys[index.column()]]
            if keys[index.column()] == "amount":
                return f"{value:.2f} DA"
            return str(value) if value else ""
        return None

    def rowCount(self, index): return len(self._data)
    def columnCount(self, index): return len(self.headers)
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal: return self.headers[section]
        return None

class SupplierLedgerDialog(QDialog):
    def __init__(self, supplier_id, parent=None):
        super().__init__(parent)
        self.supplier_id = supplier_id
        self.supplier = SupplierModel.get_supplier(supplier_id)
        
        self.setWindowTitle(f"Ledger - {self.supplier['name']}")
        self.setMinimumWidth(600)
        self.setMinimumHeight(600)

        layout = QVBoxLayout(self)

        # 1. Supplier Info & Balance
        info_group = QGroupBox("Informations Fournisseur")
        info_layout = QFormLayout()
        info_layout.addRow("Contact:", QLabel(self.supplier['contact_person'] or "N/A"))
        info_layout.addRow("Téléphone:", QLabel(self.supplier['phone'] or "N/A"))
        
        self.balance_label = QLabel()
        self.update_balance_label()
        info_layout.addRow("Solde Global Dû:", self.balance_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # 2. Add Transaction Form
        trans_group = QGroupBox("Nouvelle Transaction")
        trans_layout = QHBoxLayout()
        
        self.trans_type = QComboBox()
        self.trans_type.addItems(["Facture", "Versement"])
        
        self.trans_amount = QDoubleSpinBox()
        self.trans_amount.setRange(0, 99999999)
        self.trans_amount.setSuffix(" DA")
        
        self.trans_note = QLineEdit()
        self.trans_note.setPlaceholderText("Note (ex: Facture #1023)")
        
        add_btn = QPushButton("Ajouter")
        add_btn.setObjectName("primary")
        add_btn.setStyleSheet("""
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
        add_btn.clicked.connect(self.add_transaction)
        
        trans_layout.addWidget(QLabel("Type:"))
        trans_layout.addWidget(self.trans_type)
        trans_layout.addWidget(QLabel("Montant:"))
        trans_layout.addWidget(self.trans_amount)
        trans_layout.addWidget(self.trans_note)
        trans_layout.addWidget(add_btn)
        
        trans_group.setLayout(trans_layout)
        layout.addWidget(trans_group)

        # 3. Transaction History Table
        self.table = QTableView()
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setEditTriggers(QTableView.NoEditTriggers)
        self.table.horizontalHeader().stretchLastSection = True
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        self.load_transactions()

    def update_balance_label(self):
        balance = self.supplier['balance_due'] or 0.0
        color = "#DC2626" if balance > 0 else "#16A34A"
        self.balance_label.setText(f"<span style='color:{color}; font-weight:bold; font-size:16px;'>{balance:.2f} DA</span>")

    def add_transaction(self):
        amount = self.trans_amount.value()
        if amount <= 0:
            QMessageBox.warning(self, "Erreur", "Le montant doit être supérieur à 0.")
            return
            
        SupplierModel.add_transaction(
            self.supplier_id, 
            self.trans_type.currentText(), 
            amount, 
            self.trans_note.text().strip()
        )
        
        # Refresh data
        self.supplier = SupplierModel.get_supplier(self.supplier_id)
        self.update_balance_label()
        self.load_transactions()
        
        # Reset inputs
        self.trans_amount.setValue(0)
        self.trans_note.clear()

    def load_transactions(self):
        transactions = SupplierModel.get_transactions(self.supplier_id)
        self.model = TransactionTableModel(transactions)
        self.table.setModel(self.model)