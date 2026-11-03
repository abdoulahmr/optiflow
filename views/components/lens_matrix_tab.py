# views/components/lens_matrix_tab.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                               QDoubleSpinBox, QPushButton, QHeaderView, QAbstractItemView, 
                               QHBoxLayout, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from models.lens_model import LensModel
from views.components.lens_stock_dialog import LensStockDialog

class LensMatrixTab(QWidget):
    def __init__(self, lens_type):
        super().__init__()
        self.lens_type = lens_type
        self.price_mode = "retail"
        self.cells = []
        self.is_editing = False
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(55)
        self.table.setStyleSheet("QTableView::item { padding: 0px; border-bottom: 1px solid #F3F4F6; }")
        
        self.columns = LensModel.get_all_treatments()
        
        self.table.setColumnCount(1 + len(self.columns))
        headers = ["Groupe"] + self.columns
        self.table.setHorizontalHeaderLabels(headers)
        
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setMinimumSectionSize(120)
        for i in range(1, len(self.columns) + 1):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)

        layout.addWidget(self.table)
        self.load_data()

    def set_price_mode(self, mode):
        self.price_mode = mode
        self.load_data()

    def set_edit_mode(self, enabled):
        self.is_editing = enabled
        for cell in self.cells:
            # Toggle price spinbox
            spin = cell['price_spin']
            spin.setReadOnly(not enabled)
            if enabled:
                spin.setStyleSheet("QDoubleSpinBox { border: 1px solid #2563EB; background: #EFF6FF; border-radius: 4px; padding: 6px; font-weight: bold; }")
            else:
                spin.setStyleSheet("QDoubleSpinBox { border: none; background: transparent; padding: 6px; font-weight: bold; color: #111827; }")
            
            # Toggle stock button
            stock_btn = cell['stock_btn']
            stock_btn.setEnabled(enabled)
            if enabled:
                stock_btn.setStyleSheet("""
                    QPushButton {
                        border: 1px solid #16A34A; background: #F0FDF4;
                        border-radius: 4px; color: #16A34A; font-weight: bold; padding: 4px;
                    }
                    QPushButton:hover { background: #DCFCE7; }
                """)
            else:
                # Disabled style: greyed out
                stock_btn.setStyleSheet("""
                    QPushButton {
                        border: 1px solid #D1D5DB; background: #F3F4F6;
                        border-radius: 4px; color: #9CA3AF; font-weight: bold; padding: 4px;
                    }
                """)

    def get_changed_data(self):
        data = []
        for cell in self.cells:
            data.append({
                'id': cell['id'],
                'price': cell['price_spin'].value(),
                'type': self.price_mode
            })
        return data

    def load_data(self):
        self.cells.clear()
        # Simple query - no JOIN, no stock fetching
        lenses = LensModel.get_lenses(self.lens_type)
        if not lenses: return
            
        groups = {}
        for lens in lenses:
            g = lens['optical_group']
            if g not in groups:
                groups[g] = {}
            groups[g][lens['treatment']] = lens

        self.table.setRowCount(len(groups))
        header_font = QFont()
        header_font.setBold(True)

        for r, (group_name, data) in enumerate(groups.items()):
            self.table.setRowHeight(r, 55)
            
            # Col 0: Group Name
            item = QTableWidgetItem(group_name)
            item.setTextAlignment(Qt.AlignCenter)
            item.setFont(header_font)
            self.table.setItem(r, 0, item)
            
            col = 1
            for col_name in self.columns:
                lens = data.get(col_name)
                
                cell_widget = QFrame()
                cell_layout = QHBoxLayout(cell_widget)
                cell_layout.setContentsMargins(4, 2, 4, 2)
                cell_layout.setSpacing(4)
                
                # Price SpinBox
                price_spin = QDoubleSpinBox()
                price_spin.setRange(0, 999999)
                price_spin.setSuffix(" DA")
                price_spin.setAlignment(Qt.AlignCenter)
                price_spin.setButtonSymbols(QDoubleSpinBox.NoButtons)
                price_spin.setReadOnly(True)
                price_spin.setStyleSheet("QDoubleSpinBox { border: none; background: transparent; padding: 4px; font-weight: bold; color: #111827; }")
                
                # Stock Button - shows just "Stock", no count
                stock_btn = QPushButton("Stock")
                stock_btn.setFixedWidth(70)
                stock_btn.setCursor(Qt.PointingHandCursor)
                
                if lens:
                    value = lens['retail_price'] if self.price_mode == "retail" else lens['cost_price']
                    price_spin.setValue(value if value else 0.0)
                    
                    # Style based on edit mode (no stock fetching!)
                    if not self.is_editing:
                        stock_btn.setEnabled(False)
                        stock_btn.setStyleSheet("""
                            QPushButton {
                                border: 1px solid #D1D5DB; background: #F3F4F6;
                                border-radius: 4px; color: #9CA3AF; font-weight: bold; padding: 4px;
                            }
                        """)
                    else:
                        stock_btn.setStyleSheet("""
                            QPushButton {
                                border: 1px solid #16A34A; background: #F0FDF4;
                                border-radius: 4px; color: #16A34A; font-weight: bold; padding: 4px;
                            }
                            QPushButton:hover { background: #DCFCE7; }
                        """)
                    
                    # Connect button to open dialog
                    desc = f"{lens['optical_group']} - {lens['treatment']} ({lens['type']})"
                    stock_btn.clicked.connect(lambda checked, lid=lens['id'], d=desc: self.open_stock_dialog(lid, d))
                    
                    self.cells.append({'id': lens['id'], 'price_spin': price_spin, 'stock_btn': stock_btn})
                
                cell_layout.addWidget(price_spin)
                cell_layout.addWidget(stock_btn)
                
                self.table.setCellWidget(r, col, cell_widget)
                col += 1

    def open_stock_dialog(self, lens_id, description):
        if not self.is_editing:
            return
            
        dialog = LensStockDialog(lens_id, description, self)
        dialog.exec()
        # No need to reload the matrix since we don't show stock counts anymore