# views/catalogue_tab/catalogue_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QTableView, QHeaderView, QAbstractItemView, 
                               QTabWidget, QTreeWidget, QTreeWidgetItem, QPushButton)
from PySide6.QtCore import Qt, QAbstractTableModel
from PySide6.QtGui import QFont, QColor
from database.db_manager import db
from models.inventory_model import CONTACT_LENS_TYPES

class CatalogueTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self.headers = ["Type", "Description", "Prix Vente (DA)", "Prix Achat (DA)", "Stock"]

    def data(self, index, role):
        if role == Qt.DisplayRole:
            row = self._data[index.row()]
            value = row[index.column()]
            if index.column() in [2, 3]:
                return f"{value:.2f}" if value is not None else "0.00"
            return str(value) if value is not None else ""
        elif role == Qt.ForegroundRole:
            if index.column() == 4:
                row = self._data[index.row()]
                if row[4] is not None and row[4] <= 0:
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

class CatalogueView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # 1. Header
        title = QLabel("Catalogue Général")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Recherchez et consultez tous les produits et verres")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        # 2. Shared Search Bar
        action_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search")
        self.search_input.setPlaceholderText("Rechercher dans l'onglet actuel...")
        self.search_input.textChanged.connect(self.load_data)
        action_bar.addWidget(self.search_input)
        
        # Expand/Collapse all buttons (only visible on Verres tab)
        self.expand_all_btn = QPushButton("Tout déplier")
        self.expand_all_btn.setObjectName("secondary")
        self.expand_all_btn.clicked.connect(lambda: self.expand_collapse_all(True))
        self.expand_all_btn.setVisible(False)
        
        self.collapse_all_btn = QPushButton("Tout replier")
        self.collapse_all_btn.setObjectName("secondary")
        self.collapse_all_btn.clicked.connect(lambda: self.expand_collapse_all(False))
        self.collapse_all_btn.setVisible(False)
        
        action_bar.addWidget(self.expand_all_btn)
        action_bar.addWidget(self.collapse_all_btn)
        layout.addLayout(action_bar)

        # 3. Tabs
        self.tabs = QTabWidget()
        self.tab_categories = ["Verres", "Montures", "Lentilles", "Lunettes de Soleil", "Produit de lentille", "Produits de nettoyage", "Accessoires"]
        
        self.tables = {}
        for category in self.tab_categories:
            if category == "Verres":
                # Use a TreeWidget for the lenses tab
                tree = QTreeWidget()
                tree.setHeaderLabels(["Description", "Prix Vente (DA)", "Prix Achat (DA)", "Stock Total"])
                tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
                tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
                tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
                tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
                tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
                tree.setRootIsDecorated(True)
                tree.setAnimated(True)
                tree.setUniformRowHeights(True)
                self.tables[category] = tree
                self.tabs.addTab(tree, category)
            else:
                table = QTableView()
                table.setSelectionBehavior(QTableView.SelectRows)
                table.setEditTriggers(QTableView.NoEditTriggers)
                table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
                table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
                table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
                table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
                table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
                table.verticalHeader().setVisible(False)
                self.tables[category] = table
                self.tabs.addTab(table, category)
            
        self.tabs.currentChanged.connect(self.load_data)
        layout.addWidget(self.tabs)

        self.load_data()
        # Show/hide expand buttons based on initial tab
        self.update_expand_buttons()

    def update_expand_buttons(self):
        """Show expand/collapse buttons only on the Verres tab."""
        is_verres = (self.tabs.tabText(self.tabs.currentIndex()) == "Verres")
        self.expand_all_btn.setVisible(is_verres)
        self.collapse_all_btn.setVisible(is_verres)

    def expand_collapse_all(self, expand):
        tree = self.tables.get("Verres")
        if tree:
            for i in range(tree.topLevelItemCount()):
                tree.topLevelItem(i).setExpanded(expand)

    def load_data(self):
        self.update_expand_buttons()
        search_term = f"%{self.search_input.text()}%"
        current_tab_index = self.tabs.currentIndex()
        current_category = self.tab_categories[current_tab_index]
        current_widget = self.tables[current_category]
        
        if current_category == "Verres":
            self.load_lenses_tree(current_widget, search_term)
        else:
            self.load_inventory_table(current_widget, current_category, search_term)

    def load_lenses_tree(self, tree, search_term):
        tree.clear()
        
        # Fetch all lenses with their total stock
        query = """
            SELECT 
                l.id, l.type, l.optical_group, l.treatment, 
                l.retail_price, l.cost_price,
                (SELECT COALESCE(SUM(quantity), 0) FROM lens_stock_entries WHERE lens_id = l.id) as stock_qty
            FROM lenses l
            WHERE l.retail_price > 0 
              AND (l.optical_group LIKE ? OR l.treatment LIKE ? OR l.type LIKE ?)
            ORDER BY l.optical_group, l.treatment
        """
        data = db.fetch_all(query, (search_term, search_term, search_term))
        
        # Fetch all stock entries for these lenses
        lens_ids = [lens['id'] for lens in data]
        stock_entries = {}
        if lens_ids:
            placeholders = ','.join('?' * len(lens_ids))
            entries_data = db.fetch_all(
                f"SELECT id, lens_id, sph, cyl, quantity FROM lens_stock_entries WHERE lens_id IN ({placeholders}) ORDER BY sph, cyl",
                tuple(lens_ids)
            )
            for entry in entries_data:
                if entry['lens_id'] not in stock_entries:
                    stock_entries[entry['lens_id']] = []
                stock_entries[entry['lens_id']].append(entry)
        
        bold_font = QFont()
        bold_font.setBold(True)
        bold_font.setPointSize(11)
        
        child_font = QFont()
        child_font.setPointSize(10)
        
        def fmt(v):
            """Format SPH/CYL with explicit sign: +1.50, -0.25."""
            if v >= 0:
                return f"+{v:.2f}"
            return f"{v:.2f}"
        
        # Build the tree: each lens is a parent, stock entries are children
        for lens in data:
            # Parent row: Lens info with prices and total stock
            parent_label = f"{lens['optical_group']} - {lens['treatment']} ({lens['type']})"
            
            parent_item = QTreeWidgetItem([
                parent_label,
                f"{lens['retail_price']:.2f}",
                f"{lens['cost_price']:.2f}",
                str(lens['stock_qty'])
            ])
            parent_item.setFont(0, bold_font)
            parent_item.setForeground(0, QColor("#2563EB"))
            parent_item.setBackground(0, QColor("#EFF6FF"))
            parent_item.setBackground(1, QColor("#EFF6FF"))
            parent_item.setBackground(2, QColor("#EFF6FF"))
            parent_item.setBackground(3, QColor("#EFF6FF"))
            
            # Color the stock red if 0
            if lens['stock_qty'] == 0:
                parent_item.setForeground(3, QColor("#DC2626"))
            else:
                parent_item.setForeground(3, QColor("#16A34A"))
            
            # Add child rows: each SPH/CYL stock entry
            entries = stock_entries.get(lens['id'], [])
            for entry in entries:
                child_item = QTreeWidgetItem([
                    f"   SPH {fmt(entry['sph'])}",
                    f"CYL {fmt(entry['cyl'])}",
                    f"{entry['quantity']} Unit",
                    ""
                ])
                child_item.setFont(0, child_font)
                child_item.setFont(1, child_font)
                child_item.setFont(2, child_font)
                child_item.setForeground(0, QColor("#374151"))
                child_item.setForeground(1, QColor("#374151"))
                child_item.setForeground(2, QColor("#16A34A"))
                
                parent_item.addChild(child_item)
            
            # If no stock entries, show a placeholder child
            if not entries:
                no_stock_item = QTreeWidgetItem([
                    "   (Aucun stock enregistré)",
                    "",
                    "",
                    ""
                ])
                no_stock_item.setFont(0, child_font)
                no_stock_item.setForeground(0, QColor("#9CA3AF"))
                parent_item.addChild(no_stock_item)
            
            # Auto-expand if there's a search term
            if search_term != "%%":
                parent_item.setExpanded(True)
            else:
                parent_item.setExpanded(False)
            
            tree.addTopLevelItem(parent_item)

    def load_inventory_table(self, table, category, search_term):
        if category == "Lentilles":
            # Fetch all contact lens subtypes
            placeholders = ','.join('?' * len(CONTACT_LENS_TYPES))
            query = f"""
                SELECT category as type, name as description, retail_price, cost_price, stock_qty
                FROM inventory
                WHERE category IN ({placeholders}) AND (name LIKE ?)
                ORDER BY name ASC
            """
            params = list(CONTACT_LENS_TYPES) + [search_term]
            data = db.fetch_all(query, tuple(params))
        else:
            query = """
                SELECT category as type, name as description, retail_price, cost_price, stock_qty
                FROM inventory
                WHERE category = ? AND (name LIKE ?)
                ORDER BY name ASC
            """
            data = db.fetch_all(query, (category, search_term))
            
        table.setModel(CatalogueTableModel(data))