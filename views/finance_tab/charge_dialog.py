# views/finance_tab/charge_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                               QDoubleSpinBox, QPushButton, 
                               QHBoxLayout, QMessageBox)
from PySide6.QtCore import Qt
from models.charge_model import ChargeModel

class ChargeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter une Dépense")
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Ex: Loyer du mois")
        
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Ex: Loyer, Électricité, Salaires")
        
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 99999999)
        self.amount_input.setSuffix(" DA")
        
        form.addRow("Description *:", self.desc_input)
        form.addRow("Catégorie:", self.category_input)
        form.addRow("Montant *:", self.amount_input)
        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setObjectName("secondary")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Enregistrer")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #2563EB;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 11px 18px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #1D4ED8;
            }
        """)
        save_btn.setObjectName("primary")
        save_btn.clicked.connect(self.save_charge)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def save_charge(self):
        desc = self.desc_input.text().strip()
        amount = self.amount_input.value()
        
        if not desc or amount <= 0:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une description et un montant valides.")
            return
            
        data = {
            'description': desc,
            'category': self.category_input.text().strip(),
            'amount': amount
        }
        ChargeModel.add_charge(data)
        self.accept()