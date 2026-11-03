# views/inventory_tab/restock_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLabel, 
                               QSpinBox, QPushButton, QHBoxLayout)
from models.inventory_model import InventoryModel

class RestockDialog(QDialog):
    def __init__(self, item_id, parent=None):
        super().__init__(parent)
        self.item_id = item_id
        self.item = InventoryModel.get_item_by_id(item_id)
        
        self.setWindowTitle(f"Approvisionner - {self.item['name']}")
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        current_stock = self.item['stock_qty'] or 0
        info_label = QLabel(f"Stock actuel: <b>{current_stock}</b>")
        
        self.qty_input = QSpinBox()
        self.qty_input.setRange(1, 9999)
        self.qty_input.setValue(1)
        
        form.addRow("Quantité à ajouter:", self.qty_input)
        layout.addWidget(info_label)
        layout.addLayout(form)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setObjectName("secondary")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Mettre à jour le Stock")
        save_btn.setStyleSheet("""
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
        save_btn.setObjectName("primary")
        save_btn.clicked.connect(self.save_restock)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def save_restock(self):
        qty = self.qty_input.value()
        InventoryModel.restock_item(self.item_id, qty)
        self.accept()