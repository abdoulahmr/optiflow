# views/inventory_tab/inventory_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QTableView, QComboBox, 
                               QHeaderView, QMessageBox, QApplication, QAbstractItemView)
from PySide6.QtCore import Qt, QAbstractTableModel
from models.inventory_model import InventoryModel, CONTACT_LENS_TYPES
from views.inventory_tab.inventory_dialog import InventoryDialog
from styles import StatCard
from database.db_manager import db

class InventoryTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self.headers = ["Barcode", "Nom", "Catégorie", "Stock", "Prix Achat", "Prix Vente", "Seuil"]

    def data(self, index, role):
        if role == Qt.DisplayRole:
            row = self._data[index.row()]
            keys = ["barcode", "name", "category", "stock_qty", "cost_price", "retail_price", "seuil"]
            value = row[keys[index.column()]]
            if keys[index.column()] in ["cost_price", "retail_price"]:
                return f"{value:.2f} DA"
            return str(value) if value is not None else ""
        elif role == Qt.ForegroundRole:
            row = self._data[index.row()]
            if row['stock_qty'] == 0 or row['stock_qty'] <= row['seuil']:
                if index.column() == 3:
                    return Qt.red
        return None

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self.headers)

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

class InventoryView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        title = QLabel("Gestion du Stock")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Montures, Lentilles et Accessoires")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        # KPI Dashboard
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(15)
        self.card_refs = StatCard("Total Références", "0", "Articles enregistrés")
        self.card_value = StatCard("Valeur du Stock (Achat)", "0 DA", "Investissement total", "#2563EB")
        self.card_low = StatCard("Stock Faible", "0", "En dessous du seuil", "#D97706")
        self.card_out = StatCard("Rupture de Stock", "0", "Produits épuisés", "#DC2626")
        kpi_layout.addWidget(self.card_refs)
        kpi_layout.addWidget(self.card_value)
        kpi_layout.addWidget(self.card_low)
        kpi_layout.addWidget(self.card_out)
        layout.addLayout(kpi_layout)

        # Action Bar
        action_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search")
        self.search_input.setPlaceholderText("Rechercher par nom ou code-barres...")
        self.search_input.textChanged.connect(self.load_inventory)
        
        self.category_filter = QComboBox()
        self.category_filter.addItems([
            "Tous", "Montures", "Lunettes de Soleil", "Lentilles",
            "Produit de lentille", "Produits de nettoyage", "Accessoires"
        ])
        self.category_filter.currentTextChanged.connect(self._on_category_filter_changed)
        
        self.cl_type_filter = QComboBox()
        self.cl_type_filter.addItems(["Toutes les lentilles"] + CONTACT_LENS_TYPES)
        self.cl_type_filter.currentTextChanged.connect(self.load_inventory)
        self.cl_type_filter.setVisible(False)
        
        self.add_btn = QPushButton("＋ Ajouter Produit")
        self.add_btn.setObjectName("primary")
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
        self.add_btn.clicked.connect(self.open_add_dialog)
        
        action_bar.addWidget(self.search_input)
        action_bar.addWidget(self.category_filter)
        action_bar.addWidget(self.cl_type_filter)
        action_bar.addWidget(self.add_btn)
        layout.addLayout(action_bar)

        # Table
        self.table = QTableView()
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)
        self.table.setEditTriggers(QTableView.NoEditTriggers)
        self.table.horizontalHeader().stretchLastSection = True
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        self.load_inventory()

    def _on_category_filter_changed(self, category):
        is_lentilles = (category == "Lentilles")
        self.cl_type_filter.setVisible(is_lentilles)
        if not is_lentilles and self.cl_type_filter.currentText() != "Toutes les lentilles":
            self.cl_type_filter.setCurrentText("Toutes les lentilles")
        else:
            self.load_inventory()

    def load_inventory(self):
        search = self.search_input.text()
        category = self.category_filter.currentText()
        
        if category == "Lentilles":
            cl_type = self.cl_type_filter.currentText()
            if cl_type == "Toutes les lentilles":
                placeholders = ','.join('?' * len(CONTACT_LENS_TYPES))
                query = f"SELECT * FROM inventory WHERE category IN ({placeholders}) AND (name LIKE ? OR barcode LIKE ?) ORDER BY name ASC"
                params = list(CONTACT_LENS_TYPES) + [f"%{search}%", f"%{search}%"]
                items = db.fetch_all(query, tuple(params))
            else:
                query = "SELECT * FROM inventory WHERE category = ? AND (name LIKE ? OR barcode LIKE ?) ORDER BY name ASC"
                items = db.fetch_all(query, (cl_type, f"%{search}%", f"%{search}%"))
        else:
            items = InventoryModel.get_all_items(search, category)
        
        self.model = InventoryTableModel(items)
        self.table.setModel(self.model)
        
        kpis = InventoryModel.get_kpis()
        self.card_refs.value_label.setText(str(kpis['total_refs']))
        self.card_value.value_label.setText(kpis['total_value'])
        self.card_low.value_label.setText(str(kpis['low_stock']))
        self.card_out.value_label.setText(str(kpis['out_stock']))

    def open_add_dialog(self):
        dialog = InventoryDialog(self)
        if dialog.exec():
            self.load_inventory()
            app = QApplication.instance()
            app.catalogue_dirty = True

    def open_edit_dialog(self, item_id):
        dialog = InventoryDialog(self, item_id)
        if dialog.exec():
            self.load_inventory()
            app = QApplication.instance()
            app.catalogue_dirty = True

    def delete_item(self, item_id):
        confirm = QMessageBox.question(self, "Confirmer", "Êtes-vous sûr de vouloir supprimer ce produit ?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            InventoryModel.delete_item(item_id)
            self.load_inventory()
            app = QApplication.instance()
            app.catalogue_dirty = True