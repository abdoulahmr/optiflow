# views/patients_tab/patient_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                               QComboBox, QDateEdit, QTextEdit, QPushButton, 
                               QHBoxLayout, QMessageBox)
from PySide6.QtCore import QDate
from models.patient_model import PatientModel
from models.contact_lens_model import ContactLensModel
from views.components.contact_lens_grid import ContactLensGrid
from database.db_manager import db

class PatientDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nouvelle Fiche Client")
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)  
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Inputs
        self.nom_input = QLineEdit()
        self.prenom_input = QLineEdit()
        
        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDisplayFormat("yyyy-MM-dd")
        self.dob_input.setDate(QDate(2000, 1, 1))

        self.gender_input = QComboBox()
        self.gender_input.addItems(["Homme", "Femme"])
        
        self.phone_input = QLineEdit()
        self.phone_input.setInputMask("00 00 00 00 00;_")
        
        self.address_input = QTextEdit()
        self.address_input.setFixedHeight(60)

        # Add to form
        form_layout.addRow("Nom *:", self.nom_input)
        form_layout.addRow("Prénom *:", self.prenom_input)
        form_layout.addRow("Date de Naissance:", self.dob_input)
        form_layout.addRow("Genre:", self.gender_input)
        form_layout.addRow("Téléphone:", self.phone_input)
        form_layout.addRow("Adresse:", self.address_input)

        layout.addLayout(form_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.setObjectName("secondary")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Enregistrer")
        self.save_btn.setObjectName("primary")
        self.save_btn.setStyleSheet("""
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
        self.save_btn.clicked.connect(self.save_patient)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

    def save_patient(self):
        nom = self.nom_input.text().strip()
        prenom = self.prenom_input.text().strip()

        if not nom or not prenom:
            QMessageBox.warning(self, "Erreur", "Le Nom et le Prénom sont obligatoires.")
            return

        data = {
            'nom': nom,
            'prenom': prenom,
            'date_of_birth': self.dob_input.date().toString("yyyy-MM-dd"),
            'gender': self.gender_input.currentText(),
            'phone': self.phone_input.text().strip(),
            'address': self.address_input.toPlainText().strip()
        }

        PatientModel.add_patient(data)
        self.accept() 