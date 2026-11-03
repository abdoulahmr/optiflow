# views/finance_tab/expenses_history_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTableView, QHeaderView, 
                               QAbstractItemView, QPushButton, QHBoxLayout, 
                               QLineEdit, QLabel, QDateEdit) 
from PySide6.QtCore import Qt, QAbstractTableModel, QDate 
from models.charge_model import ChargeModel

class ExpensesTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self.headers = ["ID", "Date", "Description", "Catégorie", "Montant (DA)"]

    def data(self, index, role):
        if role == Qt.DisplayRole:
            row = self._data[index.row()]
            keys = ["id", "date", "description", "category", "amount"]
            value = row[keys[index.column()]]
            if keys[index.column()] == "amount":
                return f"{value:.2f}" if value is not None else "0.00"
            return str(value) if value is not None else ""
        elif role == Qt.ForegroundRole:
            # Make amount red since it's an expense
            if index.column() == 4:
                return Qt.red
        return None

    def rowCount(self, index): return len(self._data)
    def columnCount(self, index): return len(self.headers)
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal: return self.headers[section]
        return None

class ExpensesHistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Historique Complet des Dépenses")
        self.resize(900, 500)

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
        
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search")
        self.search_input.setPlaceholderText("Filter by Category or Description...")
        self.search_input.textChanged.connect(self.load_data)
        
        filter_layout.addWidget(QLabel("From:"))
        filter_layout.addWidget(self.start_date)
        filter_layout.addWidget(QLabel("To:"))
        filter_layout.addWidget(self.end_date)
        filter_layout.addWidget(self.search_input, 1)
        layout.addLayout(filter_layout)

        # Table
        self.table = QTableView()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().stretchLastSection = True
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

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
        s_date = self.start_date.date().toString("yyyy-MM-dd")
        e_date = self.end_date.date().toString("yyyy-MM-dd")
        
        charges = ChargeModel.get_all_charges(search, s_date, e_date)
        self.model = ExpensesTableModel(charges)
        self.table.setModel(self.model)