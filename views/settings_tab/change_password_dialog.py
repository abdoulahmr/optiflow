# views/settings_tab/change_password_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                               QPushButton, QHBoxLayout, QMessageBox)
from PySide6.QtCore import Qt

class ChangePasswordDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Changer le mot de passe - {username}")
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.new_pass_input = QLineEdit()
        self.new_pass_input.setEchoMode(QLineEdit.Password)
        
        self.confirm_pass_input = QLineEdit()
        self.confirm_pass_input.setEchoMode(QLineEdit.Password)
        
        form.addRow("Nouveau mot de passe:", self.new_pass_input)
        form.addRow("Confirmer:", self.confirm_pass_input)
        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setObjectName("secondary")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Mettre à jour")
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
        save_btn.clicked.connect(self.save_password)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def save_password(self):
        new_pass = self.new_pass_input.text()
        confirm_pass = self.confirm_pass_input.text()
        
        if not new_pass:
            QMessageBox.warning(self, "Erreur", "Le mot de passe ne peut pas être vide.")
            return
            
        if new_pass != confirm_pass:
            QMessageBox.warning(self, "Erreur", "Les mots de passe ne correspondent pas.")
            return
            
        self.accept()