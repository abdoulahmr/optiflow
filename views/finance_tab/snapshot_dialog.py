# views/finance_tab/snapshot_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTableView, QHeaderView, QAbstractItemView, 
                               QComboBox, QDateEdit, QMessageBox, QGroupBox, QFormLayout)
from PySide6.QtCore import Qt, QAbstractTableModel, QDate
from models.snapshot_model import SnapshotModel
from styles import PRIMARY, PRIMARY_HOVER

class SnapshotsTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self.headers = ["Type", "Période", "CA Total", "Profit Réalisé", "Dépenses", "Profit Net", "Valeur Stock", "Dettes", "Date de Clôture"]

    def data(self, index, role):
        if role == Qt.DisplayRole:
            row = self._data[index.row()]
            keys = ["period_type", "period_value", "revenue", "realized_profit", "total_charges", "net_profit", "stock_value", "total_debt", "date_saved"]
            value = row[keys[index.column()]]
            
            if index.column() == 0:
                return "Mensuel" if value == "monthly" else "Annuel"
            elif index.column() in [2, 3, 4, 5, 6, 7]:
                return f"{value:,.0f} DA" if value is not None else "0 DA"
            return str(value) if value is not None else ""
        return None

    def rowCount(self, index): return len(self._data)
    def columnCount(self, index): return len(self.headers)
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal: return self.headers[section]
        return None

class SnapshotDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Clôtures Mensuelles & Annuelles")
        self.resize(1000, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 1. Generate Snapshot Section
        gen_group = QGroupBox("Générer une Clôture (Instantané)")
        gen_layout = QHBoxLayout(gen_group)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Mensuel", "Annuel"])
        
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.date_input.setDate(QDate.currentDate())
        
        generate_btn = QPushButton("💾 Générer et Sauvegarder")
        generate_btn.setStyleSheet(f"QPushButton {{ background: {PRIMARY}; color: white; border: none; border-radius: 8px; padding: 10px 16px; font-weight: 600; }} QPushButton:hover {{ background: {PRIMARY_HOVER}; }}")
        generate_btn.setCursor(Qt.PointingHandCursor)
        generate_btn.clicked.connect(self.generate_snapshot)
        
        gen_layout.addWidget(QLabel("Type:"))
        gen_layout.addWidget(self.type_combo)
        gen_layout.addWidget(QLabel("Date:"))
        gen_layout.addWidget(self.date_input)
        gen_layout.addStretch()
        gen_layout.addWidget(generate_btn)
        
        layout.addWidget(gen_group)

        # 2. History Table
        layout.addWidget(QLabel("Historique des Clôtures"))
        
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
        snapshots = SnapshotModel.get_all_snapshots()
        self.model = SnapshotsTableModel(snapshots)
        self.table.setModel(self.model)

    def generate_snapshot(self):
        date = self.date_input.date()
        period_type = "monthly" if self.type_combo.currentText() == "Mensuel" else "annual"
        
        if period_type == "monthly":
            period_value = date.toString("yyyy-MM")
        else:
            period_value = date.toString("yyyy")
            
        SnapshotModel.save_snapshot(period_type, period_value)
        QMessageBox.information(self, "Succès", f"Clôture {period_value} enregistrée avec succès.")
        self.load_data()