# views/finance_tab/sales_history_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTableView, QHeaderView, 
                               QAbstractItemView, QPushButton, QHBoxLayout, 
                               QMessageBox, QTableWidget, QTableWidgetItem, 
                               QLineEdit, QComboBox, QLabel, QWidget, QDateEdit) 
from PySide6.QtCore import Qt, QAbstractTableModel, QDate, QModelIndex 
from PySide6.QtGui import QFont, QColor
from models.finance_model import FinanceModel
from models.pos_model import POSModel
from models.patient_model import PatientModel
from database.db_manager import db
from views.pos_tab.settle_debt_dialog import SettleDebtDialog
from views.components.receipt_view import ReceiptViewDialog
from styles import PRIMARY, PRIMARY_HOVER

class FullSalesTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self.headers = ["ID", "Date", "Client", "ID Ticket", "Total (DA)", 
                        "Versé (DA)", "Reste (DA)", "Statut", "Action"]

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # Action column (index 8) - leave empty, button is set via setIndexWidget
            if index.column() == 8:
                return ""
            
            row = self._data[index.row()]
            keys = ["id", "created_at", "patient_name", "client_id_text", 
                    "total_payable", "deposit_received", "remaining_balance", "status"]
            value = row[keys[index.column()]]
            
            # Format date (show only YYYY-MM-DD)
            if keys[index.column()] == "created_at" and value:
                return str(value)[:10]
            # Format currency columns
            if keys[index.column()] in ["total_payable", "deposit_received", "remaining_balance"]:
                return f"{value:.2f}" if value is not None else "0.00"
            return str(value) if value is not None else ""
            
        elif role == Qt.ForegroundRole:
            row = self._data[index.row()]
            # Reste (DA) column - red if > 0, green if 0
            if index.column() == 6:
                if row['remaining_balance'] > 0:
                    return QColor("#DC2626")
                else:
                    return QColor("#16A34A")
            # Statut column - color based on status
            elif index.column() == 7:
                if row['status'] == 'Livré':
                    return QColor("#16A34A")
                else:
                    return QColor("#D97706")
        elif role == Qt.FontRole:
            # Make Reste and Statut columns bold
            if index.column() in [6, 7]:
                font = QFont()
                font.setBold(True)
                return font
        return None

    def rowCount(self, index): return len(self._data)
    def columnCount(self, index): return len(self.headers)
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal: return self.headers[section]
        return None

class SalesHistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Historique Complet des Ventes")
        self.resize(1300, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Filters Bar
        filter_layout = QHBoxLayout()
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.start_date.dateChanged.connect(self.load_data)
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.setDate(QDate.currentDate())
        self.end_date.dateChanged.connect(self.load_data)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Tous", "En cours", "Livré"])
        self.status_filter.currentTextChanged.connect(self.load_data)
        
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search")
        self.search_input.setPlaceholderText("Client or ID Ticket...")
        self.search_input.textChanged.connect(self.load_data)
        
        filter_layout.addWidget(QLabel("From:"))
        filter_layout.addWidget(self.start_date)
        filter_layout.addWidget(QLabel("To:"))
        filter_layout.addWidget(self.end_date)
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.status_filter)
        filter_layout.addWidget(self.search_input, 1)
        layout.addLayout(filter_layout)

        # Table
        self.table = QTableView()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # Don't stretch last section so Action column stays fixed width
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self.show_order_details)
        layout.addWidget(self.table)

        # Hint label
        hint = QLabel("Double-click 'En cours' to settle debt  |  Click to view/print receipt")
        hint.setStyleSheet("color: #6B7280; font-size: 12px; font-style: italic;")
        layout.addWidget(hint)

        # Close Button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Fermer")
        close_btn.setObjectName("primary")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        self.load_data()

    def load_data(self):
        search = self.search_input.text()
        status = self.status_filter.currentText()
        s_date = self.start_date.date().toString("yyyy-MM-dd")
        e_date = self.end_date.date().toString("yyyy-MM-dd")
        
        history = FinanceModel.get_sales_history(search, status, s_date, e_date)
        self.model = FullSalesTableModel(history)
        self.table.setModel(self.model)
        
        # Set column widths after model is set
        # Action column (last, index 8) - fixed width to fit button
        self.table.horizontalHeader().setSectionResizeMode(8, QHeaderView.Fixed)
        self.table.horizontalHeader().resizeSection(8, 100)
        # ID column - small
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        # Client column - stretch to fill space
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        # Other columns - fit content
        for i in [1, 3, 4, 5, 6, 7]:
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        # Add print buttons to the Action column
        self.add_print_buttons()

    def add_print_buttons(self):
        """Adds a print button to each row in the Action column."""
        for row in range(self.model.rowCount(QModelIndex())):
            order_id = self.model._data[row]["id"]
            
            print_btn = QPushButton("Reçu")
            print_btn.setFixedHeight(30)
            print_btn.setCursor(Qt.PointingHandCursor)
            print_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {PRIMARY}; color: white; border: none;
                    border-radius: 6px; padding: 4px 10px;
                    font-weight: 600; font-size: 11px;
                }}
                QPushButton:hover {{ background: {PRIMARY_HOVER}; }}
            """)
            print_btn.clicked.connect(lambda checked, oid=order_id: self.print_receipt(oid))
            
            index = self.model.index(row, 8)
            self.table.setIndexWidget(index, print_btn)

    def print_receipt(self, order_id):
        """Opens the receipt preview dialog for the selected order."""
        # Fetch order data
        order = db.fetch_one("SELECT * FROM orders WHERE id=?", (order_id,))
        if not order:
            QMessageBox.warning(self, "Erreur", "Commande introuvable.")
            return
        
        # Fetch patient data
        patient = PatientModel.get_patient(order['patient_id'])
        if not patient:
            QMessageBox.warning(self, "Erreur", "Patient introuvable.")
            return
        
        # Fetch order items (filter out payment entries - those have negative prices)
        items_raw = FinanceModel.get_order_items(order_id)
        cart_items = []
        for item in items_raw:
            if item['price'] >= 0:  # Skip "Versement" entries
                cart_items.append({
                    'type': item['item_type'],
                    'description': item['description'],
                    'price': item['price'],
                    'discount': item['discount'] or 0.0
                })
        
        if not cart_items:
            QMessageBox.information(self, "Reçu", "Aucun article à afficher pour cette commande.")
            return
        
        # Build order_data dict for receipt
        order_data = {
            'client_id': order['client_id_text'],
            'total_payable': order['total_payable'],
            'deposit_received': order['deposit_received'],
            'remaining_balance': order['remaining_balance'],
            'payment_method': order['payment_method'] or 'N/A',
            'status': order['status']
        }
        
        # Open the receipt preview dialog
        dialog = ReceiptViewDialog(order_data, patient, cart_items, self)
        dialog.exec()

    def show_order_details(self, index):
        row = index.row()
        order_id = self.model._data[row]["id"]
        status = self.model._data[row]["status"]
        remaining = self.model._data[row]["remaining_balance"]
        
        # If the order has a remaining balance, offer to settle the debt
        if status == "En cours" and remaining > 0.01:
            reply = QMessageBox.question(
                self, 
                "Commande En Cours",
                f"Cette commande a un reste à payer de {remaining:,.2f} DA.\n\n"
                f"Voulez-vous enregistrer un nouveau paiement ?",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                dialog = SettleDebtDialog(order_id, self)
                if dialog.exec():
                    self.load_data()
            return
        
        # Otherwise, show the regular order items dialog
        items = FinanceModel.get_order_items(order_id)
        
        if not items:
            QMessageBox.information(self, "Détails", "Aucun article trouvé pour cette commande.")
            return
            
        details_dialog = QDialog(self)
        details_dialog.setWindowTitle(f"Détails de la Commande #{order_id}")
        details_dialog.setMinimumWidth(500)
        details_layout = QVBoxLayout(details_dialog)
        
        details_table = QTableWidget()
        details_table.setColumnCount(4)
        details_table.setHorizontalHeaderLabels(["Type", "Description", "Prix (DA)", "Remise (DA)"])
        details_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        details_table.verticalHeader().setVisible(False)
        details_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        details_table.setRowCount(len(items))
        
        for r, item in enumerate(items):
            details_table.setItem(r, 0, QTableWidgetItem(item['item_type']))
            details_table.setItem(r, 1, QTableWidgetItem(item['description']))
            details_table.setItem(r, 2, QTableWidgetItem(f"{item['price']:.2f}"))
            details_table.setItem(r, 3, QTableWidgetItem(f"{item['discount']:.2f}"))
            
        details_layout.addWidget(details_table)
        
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(details_dialog.accept)
        details_layout.addWidget(close_btn)
        
        details_dialog.exec()