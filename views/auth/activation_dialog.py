# views/auth/activation_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QMessageBox, QHBoxLayout, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from utils.license_client import LicenseClient
from models.settings_model import SettingsModel
from config import LICENSE_SERVER_URL, LICENSE_API_TOKEN

class ActivationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OptiFlow - Activation de Licence")
        self.setFixedSize(450, 480)
        self.client = LicenseClient(LICENSE_SERVER_URL, LICENSE_API_TOKEN)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 20)
        layout.setSpacing(10)

        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/logo.png")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # Title
        title = QLabel("Activation Requise")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2563EB;")
        
        # Trial status banner
        self.trial_banner = QLabel()
        self.trial_banner.setAlignment(Qt.AlignCenter)
        self.trial_banner.setStyleSheet("""
            QLabel {
                background: #EFF6FF; color: #2563EB;
                border: 1px solid #BFDBFE; border-radius: 8px;
                padding: 10px; font-size: 13px; font-weight: 600;
            }
        """)
        
        subtitle = QLabel("Entrez votre clé de licence pour activer OptiFlow")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #6B7280; font-size: 13px; margin-bottom: 10px;")
        
        layout.addWidget(title)
        
        # Show trial status
        trial_remaining = SettingsModel.get_trial_days_remaining()
        trial_used = SettingsModel.is_trial_used()
        if trial_remaining > 0:
            self.trial_banner.setText(f"⏳ Période d'essai: {trial_remaining} jour(s) restant(s)")
            self.trial_banner.setStyleSheet("""
                QLabel {
                    background: #ECFDF5; color: #16A34A;
                    border: 1px solid #BBF7D0; border-radius: 8px;
                    padding: 10px; font-size: 13px; font-weight: 600;
                }
            """)
            layout.addWidget(self.trial_banner)
        elif trial_used:
            self.trial_banner.setText("❌ Période d'essai expirée")
            self.trial_banner.setStyleSheet("""
                QLabel {
                    background: #FEF2F2; color: #DC2626;
                    border: 1px solid #FECACA; border-radius: 8px;
                    padding: 10px; font-size: 13px; font-weight: 600;
                }
            """)
            layout.addWidget(self.trial_banner)
        
        layout.addWidget(subtitle)

        # License key input
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("OPTI-XXXX-XXXX-XXXX")
        self.key_input.setStyleSheet("padding: 10px; font-size: 14px;")
        layout.addWidget(self.key_input)

        # Activate button
        activate_btn = QPushButton("Activer la Licence")
        activate_btn.setObjectName("primary")
        activate_btn.setCursor(Qt.PointingHandCursor)
        activate_btn.setMinimumHeight(42)
        activate_btn.setStyleSheet("""
            QPushButton {
                background: #2563EB; color: white; border: none;
                border-radius: 8px; font-weight: 600; font-size: 14px;
            }
            QPushButton:hover { background: #1D4ED8; }
        """)
        activate_btn.clicked.connect(self.attempt_activation)
        layout.addWidget(activate_btn)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background: #E5E7EB; max-height: 1px;")
        layout.addWidget(divider)
        
        # Start Trial button (only if trial not used)
        if not trial_used:
            trial_btn = QPushButton("Commencer l'essai de 7 jours")
            trial_btn.setCursor(Qt.PointingHandCursor)
            trial_btn.setMinimumHeight(40)
            trial_btn.setStyleSheet("""
                QPushButton {
                    background: white; color: #16A34A;
                    border: 2px solid #16A34A;
                    border-radius: 8px; font-weight: 600; font-size: 13px;
                }
                QPushButton:hover { background: #F0FDF4; }
            """)
            trial_btn.clicked.connect(self.start_trial)
            layout.addWidget(trial_btn)
        
        # Continue Trial button (if trial active)
        if trial_remaining > 0:
            continue_btn = QPushButton(f"➡ Continuer l'essai ({trial_remaining} jour(s) restant)")
            continue_btn.setCursor(Qt.PointingHandCursor)
            continue_btn.setMinimumHeight(40)
            continue_btn.setStyleSheet("""
                QPushButton {
                    background: #16A34A; color: white;
                    border: none; border-radius: 8px;
                    font-weight: 600; font-size: 14px;
                }
                QPushButton:hover { background: #15803D; }
            """)
            continue_btn.clicked.connect(self.continue_trial)
            layout.addWidget(continue_btn)
        
        layout.addStretch()

        # Contact Info Footer
        contact_label = QLabel(
            "Pour obtenir une licence ou en cas de problème :\n"
            "📞 Tel : +213 553 95 40 59\n"
        )
        contact_label.setAlignment(Qt.AlignCenter)
        contact_label.setStyleSheet("""
            color: #6B7280; font-size: 11px; margin-top: 10px;
            padding-top: 10px; border-top: 1px solid #E5E7EB;
        """)
        layout.addWidget(contact_label)

    def start_trial(self):
        """Starts the 7-day trial."""
        reply = QMessageBox.question(
            self, "Confirmer l'essai",
            "Voulez-vous commencer votre période d'essai de 7 jours ?\n\n"
            "Vous pourrez utiliser toutes les fonctionnalités d'OptiFlow gratuitement pendant 7 jours.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
        )
        if reply == QMessageBox.Yes:
            SettingsModel.start_trial()
            QMessageBox.information(
                self, "Essai Activé",
                "Votre période d'essai de 7 jours a commencé !\n\n"
                "Profitez d'OptiFlow sans engagement."
            )
            self.accept()

    def continue_trial(self):
        """Continues using the trial (closes dialog, allows app to launch)."""
        self.accept()

    def attempt_activation(self):
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une clé de licence.")
            return

        response, status_code = self.client.activate(key)

        if status_code == 200:
            SettingsModel.set_license_key(key)
            SettingsModel.update_setting('is_activated', 'True')
            QMessageBox.information(self, "Succès", "Licence activée avec succès ! Bienvenue sur OptiFlow.")
            self.accept()
        else:
            error_msg = response.get('error', response.get('message', 'Clé invalide ou erreur serveur.'))
            QMessageBox.critical(self, "Échec de l'activation", f"Code: {status_code}\n{error_msg}")