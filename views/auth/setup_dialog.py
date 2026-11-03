# views/auth/setup_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                               QPushButton, QHBoxLayout, QLabel, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from models.settings_model import SettingsModel
from config import resource_path

class SetupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OptiFlow - Configuration Initiale")
        self.setFixedSize(450, 500)
        self.current_user = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 40)
        layout.setSpacing(15)

        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap(resource_path("assets/logo.png"))
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # Title
        title = QLabel("Bienvenue !")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2563EB;")
        
        subtitle = QLabel("Créez votre compte Administrateur pour commencer.")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #6B7280; font-size: 14px; margin-bottom: 20px;")
        
        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Form
        form = QFormLayout()
        form.setSpacing(10)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choisissez un nom d'utilisateur")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Choisissez un mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirmez le mot de passe")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        
        form.addRow("Utilisateur:", self.username_input)
        form.addRow("Mot de passe:", self.password_input)
        form.addRow("Confirmer:", self.confirm_input)
        layout.addLayout(form)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        create_btn = QPushButton("Créer le compte")
        create_btn.setObjectName("primary")
        create_btn.setCursor(Qt.PointingHandCursor)
        create_btn.clicked.connect(self.create_account)
        
        btn_layout.addWidget(create_btn)
        layout.addLayout(btn_layout)
        layout.addStretch()

    def create_account(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Erreur", "Tous les champs sont obligatoires.")
            return
            
        if password != confirm:
            QMessageBox.warning(self, "Erreur", "Les mots de passe ne correspondent pas.")
            return
            
        SettingsModel.add_user(username, password, "Administrateur")
        self.current_user = {'username': username, 'role': 'Administrateur'}
        
        QMessageBox.information(self, "Succès", "Compte administrateur créé avec succès !")
        self.accept()