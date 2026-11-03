# views/auth/login_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                               QPushButton, QHBoxLayout, QLabel, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap 
from models.auth_model import AuthModel
from config import resource_path

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OptiFlow - Connexion")
        self.setFixedSize(400, 450)  
        self.current_user = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 40)
        layout.setSpacing(15)

        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap(resource_path("assets/logo/logo1.png"))
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # subtitle      
        subtitle = QLabel("Veuillez vous connecter pour continuer")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #6B7280; font-size: 14px; margin-bottom: 20px;")
        
        layout.addWidget(subtitle)

        # Form
        form = QFormLayout()
        form.setSpacing(10)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Entrez votre nom d'utilisateur")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Entrez votre mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        form.addRow("Utilisateur:", self.username_input)
        form.addRow("Mot de passe:", self.password_input)
        layout.addLayout(form)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.login_btn = QPushButton("Se Connecter")
        self.login_btn.setObjectName("primary")
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.clicked.connect(self.check_login)
        
        btn_layout.addWidget(self.login_btn)
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        # Pressing Enter triggers login
        self.password_input.returnPressed.connect(self.check_login)
        self.username_input.returnPressed.connect(self.check_login)

    def check_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs.")
            return
            
        user = AuthModel.login(username, password)
        if user:
            self.current_user = user
            self.accept()
        else:
            QMessageBox.critical(self, "Échec", "Nom d'utilisateur ou mot de passe incorrect.")