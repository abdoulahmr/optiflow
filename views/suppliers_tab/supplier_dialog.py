# views/suppliers_tab/supplier_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                               QPushButton, QHBoxLayout, QMessageBox, QTabWidget, 
                               QWidget, QGroupBox, QGridLayout, QLabel)
from models.supplier_model import SupplierModel

class SupplierDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nouveau Fournisseur")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)
        
        # Using a GroupBox for better UI organization
        form = QFormLayout()
        form.setSpacing(10)

        self.name_input = QLineEdit()
        self.contact_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.address_input = QLineEdit()
        self.category_input = QLineEdit() # e.g., Montures, Verres

        form.addRow("Nom de l'entreprise *:", self.name_input)
        form.addRow("Personne à contacter:", self.contact_input)
        form.addRow("Téléphone:", self.phone_input)
        form.addRow("Email:", self.email_input)
        form.addRow("Adresse:", self.address_input)
        form.addRow("Catégorie (Tag):", self.category_input)
        
        layout.addLayout(form)

        # Fiscal Compliance Group
        fiscal_group = QGroupBox("Conformité Fiscale & Financière")
        fiscal_layout = QGridLayout()
        
        self.rc_input = QLineEdit()
        self.nif_input = QLineEdit()
        self.nis_input = QLineEdit()
        self.art_input = QLineEdit()
        self.ccp_input = QLineEdit()
        self.rib_input = QLineEdit()
        
        fiscal_layout.addWidget(QLabel("RC:"), 0, 0); fiscal_layout.addWidget(self.rc_input, 0, 1)
        fiscal_layout.addWidget(QLabel("NIF:"), 0, 2); fiscal_layout.addWidget(self.nif_input, 0, 3)
        fiscal_layout.addWidget(QLabel("NIS:"), 1, 0); fiscal_layout.addWidget(self.nis_input, 1, 1)
        fiscal_layout.addWidget(QLabel("ART:"), 1, 2); fiscal_layout.addWidget(self.art_input, 1, 3)
        fiscal_layout.addWidget(QLabel("CCP:"), 2, 0); fiscal_layout.addWidget(self.ccp_input, 2, 1)
        fiscal_layout.addWidget(QLabel("Bank RIB:"), 2, 2); fiscal_layout.addWidget(self.rib_input, 2, 3)
        
        fiscal_group.setLayout(fiscal_layout)
        layout.addWidget(fiscal_group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setObjectName("secondary")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Enregistrer")
        save_btn.setObjectName("primary")
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
        save_btn.clicked.connect(self.save_supplier)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def save_supplier(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Erreur", "Le nom du fournisseur est obligatoire.")
            return

        data = {
            'name': self.name_input.text().strip(),
            'contact_person': self.contact_input.text().strip(),
            'phone': self.phone_input.text().strip(),
            'email': self.email_input.text().strip(),
            'address': self.address_input.text().strip(),
            'category_tag': self.category_input.text().strip(),
            'rc': self.rc_input.text().strip(),
            'nif': self.nif_input.text().strip(),
            'nis': self.nis_input.text().strip(),
            'art': self.art_input.text().strip(),
            'ccp': self.ccp_input.text().strip(),
            'bank_rib': self.rib_input.text().strip()
        }

        SupplierModel.add_supplier(data)
        self.accept()