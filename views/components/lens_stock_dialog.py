# views/components/lens_stock_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                                QLabel, QPushButton, QSpinBox, 
                                QTableWidget, QTableWidgetItem, QHeaderView, 
                                QAbstractItemView, QMessageBox, QGroupBox,
                                QComboBox)
from PySide6.QtCore import Qt
from models.lens_stock_model import LensStockModel
from models.lens_model import LensModel
from database.db_manager import db
from styles import PRIMARY, PRIMARY_HOVER, DANGER, BORDER, TEXT

class LensStockDialog(QDialog):
    def __init__(self, lens_id, lens_description, parent=None):
        super().__init__(parent)
        self.lens_id = lens_id
        self.lens_description = lens_description
        
        self.lens = db.fetch_one("SELECT * FROM lenses WHERE id=?", (lens_id,))
        if not self.lens:
            QMessageBox.critical(self, "Erreur", "Verre introuvable.")
            self.reject()
            return
        
        self.setWindowTitle(f"Stock - {lens_description}")
        self.setMinimumWidth(500)
        self.setMinimumHeight(450)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header showing total stock
        header_layout = QHBoxLayout()
        header_label = QLabel("Stock Total:")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.total_label = QLabel("0")
        self.total_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #16A34A;")
        header_layout.addWidget(header_label)
        header_layout.addWidget(self.total_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Add new entry group
        add_group = QGroupBox("Ajouter / Approvisionner un Stock")
        add_layout = QFormLayout(add_group)
        
        # Get valid values for this group
        sph_vals, cyl_vals = LensModel.get_valid_values_for_group(self.lens['optical_group'])
        sph_min, sph_max, cyl_min, cyl_max = LensModel.get_group_ranges(self.lens['optical_group'])
        
        # SPH dropdown
        self.sph_combo = QComboBox()
        for value, display in sph_vals:
            self.sph_combo.addItem(f"{display}", value)
        self.sph_combo.setStyleSheet(f"""
            QComboBox {{
                background: white; border: 2px solid {BORDER};
                border-radius: 8px; padding: 8px;
                font-size: 14px; font-weight: bold; color: {TEXT};
            }}
        """)
        
        # CYL dropdown
        self.cyl_combo = QComboBox()
        for value, display in cyl_vals:
            self.cyl_combo.addItem(f"{display}", value)
        self.cyl_combo.setStyleSheet(f"""
            QComboBox {{
                background: white; border: 2px solid {BORDER};
                border-radius: 8px; padding: 8px;
                font-size: 14px; font-weight: bold; color: {TEXT};
            }}
        """)
        if len(cyl_vals) <= 1:
            self.cyl_combo.setEnabled(False)

        # Quantity
        self.qty_input = QSpinBox()
        self.qty_input.setRange(1, 9999)
        self.qty_input.setValue(1)
        
        add_btn = QPushButton("＋ Ajouter au Stock")
        add_btn.setStyleSheet(f"""
            QPushButton {{ background: {PRIMARY}; color: white; border: none;
                border-radius: 8px; padding: 10px 16px; font-weight: 600; font-size: 14px; }}
            QPushButton:hover {{ background: {PRIMARY_HOVER}; }}
        """)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.add_entry)
        
        add_layout.addRow("SPH:", self.sph_combo)
        add_layout.addRow("CYL:", self.cyl_combo)
        add_layout.addRow("Quantité:", self.qty_input)
        add_layout.addRow(add_btn)
        layout.addWidget(add_group)

        # Existing entries table
        table_label = QLabel("Stocks Existantes (par SPH/CYL)")
        table_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(table_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["SPH", "CYL", "Quantité", "Action"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Fermer")
        close_btn.setStyleSheet(f"""
            QPushButton {{ background: {PRIMARY}; color: white; border: none;
                border-radius: 8px; padding: 10px 16px; font-weight: 600; }}
            QPushButton:hover {{ background: {PRIMARY_HOVER}; }}
        """)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        self.load_data()

    def format_value(self, val):
        return f"{val:+.2f}"

    def load_data(self):
        entries = LensStockModel.get_entries(self.lens_id)
        self.table.setRowCount(len(entries))
        
        for row, entry in enumerate(entries):
            self.table.setItem(row, 0, QTableWidgetItem(self.format_value(entry['sph'])))
            self.table.setItem(row, 1, QTableWidgetItem(self.format_value(entry['cyl'])))
            self.table.setItem(row, 2, QTableWidgetItem(str(entry['quantity'])))
            
            del_btn = QPushButton("🗑️")
            del_btn.setStyleSheet(f"background: transparent; color: {DANGER}; border: none; font-weight: bold;")
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.clicked.connect(lambda checked, eid=entry['id']: self.delete_entry(eid))
            self.table.setCellWidget(row, 3, del_btn)
        
        total = LensStockModel.get_total_stock(self.lens_id)
        self.total_label.setText(str(total))

    def add_entry(self):
        sph = self.sph_combo.currentData()
        cyl = self.cyl_combo.currentData()
        qty = self.qty_input.value()
        
        LensStockModel.add_entry(self.lens_id, sph, cyl, qty)
        self.qty_input.setValue(1)
        self.load_data()
        QMessageBox.information(self, "Succès", "Stock ajouté avec succès.")

    def delete_entry(self, entry_id):
        confirm = QMessageBox.question(
            self, "Confirmer", "Supprimer cette entrée de stock ?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            LensStockModel.delete_entry(entry_id)
            self.load_data()