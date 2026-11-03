# views/settings_tab/settings_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QTabWidget, QFormLayout, QLineEdit, QPushButton, 
                               QDoubleSpinBox, QTableWidget, QTableWidgetItem, 
                               QComboBox, QMessageBox, QHeaderView, QFrame, 
                               QDialog, QFileDialog, QInputDialog)  
from PySide6.QtCore import Qt
from models.settings_model import SettingsModel
from styles import StatCard
from views.settings_tab.matrix_config_widget import MatrixConfigWidget
from views.settings_tab.change_password_dialog import ChangePasswordDialog
from config import DATA_DIR  

class SettingsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        title = QLabel("Paramètres")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Configuration de l'établissement et des utilisateurs")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab 1: Store Profile
        self.tab_store = QWidget()
        store_layout = QFormLayout(self.tab_store)
        self.store_name = QLineEdit(SettingsModel.get_setting('store_name'))
        self.store_phone = QLineEdit(SettingsModel.get_setting('store_phone'))
        self.store_address = QLineEdit(SettingsModel.get_setting('store_address'))
        save_store_btn = QPushButton("Enregistrer Établissement")
        save_store_btn.setObjectName("primary")
        save_store_btn.clicked.connect(self.save_store_settings)
        store_layout.addRow("Nom de l'Établissement:", self.store_name)
        store_layout.addRow("Téléphone:", self.store_phone)
        store_layout.addRow("Adresse:", self.store_address)
        store_layout.addRow("", save_store_btn)
        self.tabs.addTab(self.tab_store, "Établissement")

        # Tab 2: Users
        self.tab_users = QWidget()
        users_layout = QVBoxLayout(self.tab_users)
        user_form = QFormLayout()
        self.user_username = QLineEdit()
        self.user_password = QLineEdit()
        self.user_password.setEchoMode(QLineEdit.Password)
        self.user_role = QComboBox()
        self.user_role.addItems(["Administrateur", "Vendeur"])
        add_user_btn = QPushButton("＋ Ajouter Utilisateur")
        add_user_btn.setStyleSheet("""
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
        add_user_btn.setObjectName("primary")
        add_user_btn.clicked.connect(self.add_user)
        user_form.addRow("Nom d'utilisateur:", self.user_username)
        user_form.addRow("Mot de passe:", self.user_password)
        user_form.addRow("Rôle:", self.user_role)
        user_form.addRow("", add_user_btn)
        users_layout.addLayout(user_form)
        
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(3)
        self.users_table.setHorizontalHeaderLabels(["ID", "Nom d'utilisateur", "Rôle"])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.users_table.verticalHeader().setVisible(False)
        self.users_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setSelectionMode(QTableWidget.SingleSelection)
        users_layout.addWidget(self.users_table)
        
        delete_user_btn = QPushButton("Supprimer Utilisateur Sélectionné")
        delete_user_btn.setStyleSheet("color: #DC2626; background: transparent; border: none;")
        delete_user_btn.clicked.connect(self.delete_user)
        users_layout.addWidget(delete_user_btn)
        change_pass_btn = QPushButton("Changer le mot de passe")
        change_pass_btn.setStyleSheet("color: #2563EB; background: transparent; border: none;")
        change_pass_btn.clicked.connect(self.change_user_password)
        users_layout.addWidget(change_pass_btn)
        self.load_users()
        self.tabs.addTab(self.tab_users, "Utilisateurs")

        # Tab 3: Backups
        self.tab_backup = QWidget()
        backup_layout = QVBoxLayout(self.tab_backup)
        backup_layout.setSpacing(15)
        
        # Header
        backup_title = QLabel("Gestion des Données")
        backup_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2563EB;")
        backup_layout.addWidget(backup_title)
        
        backup_subtitle = QLabel("Sauvegardez, exportez ou supprimez vos données en toute sécurité")
        backup_subtitle.setStyleSheet("color: #6B7280; font-size: 13px; margin-bottom: 10px;")
        backup_layout.addWidget(backup_subtitle)
        
        # === Section 1: Database Backup ===
        db_group = QFrame()
        db_group.setStyleSheet("""
            QFrame {
                background: #F0FDF4; border: 1px solid #BBF7D0;
                border-radius: 10px; padding: 15px;
            }
        """)
        db_group_layout = QVBoxLayout(db_group)
        db_group_layout.setSpacing(8)
        
        db_header = QLabel("1. Sauvegarde de la Base de Données")
        db_header.setStyleSheet("font-size: 14px; font-weight: bold; color: #16A34A;")
        db_group_layout.addWidget(db_header)
        
        db_desc = QLabel("Crée une copie complète de votre base de données SQLite (.db).\nUtile pour restaurer en cas de panne ou transfert.")
        db_desc.setStyleSheet("color: #6B7280; font-size: 12px;")
        db_desc.setWordWrap(True)
        db_group_layout.addWidget(db_desc)
        
        db_btn = QPushButton("Sauvegarder la Base de Données")
        db_btn.setMinimumHeight(42)
        db_btn.setCursor(Qt.PointingHandCursor)
        db_btn.setStyleSheet("""
            QPushButton {
                background: #16A34A; color: white; border: none;
                border-radius: 8px; padding: 10px 20px;
                font-weight: 600; font-size: 13px;
            }
            QPushButton:hover { background: #15803D; }
        """)
        db_btn.clicked.connect(self.create_db_backup)
        db_group_layout.addWidget(db_btn)
        
        backup_layout.addWidget(db_group)
        
        # === Section 2: Excel Export ===
        excel_group = QFrame()
        excel_group.setStyleSheet("""
            QFrame {
                background: #EFF6FF; border: 1px solid #BFDBFE;
                border-radius: 10px; padding: 15px;
            }
        """)
        excel_group_layout = QVBoxLayout(excel_group)
        excel_group_layout.setSpacing(8)
        
        excel_header = QLabel("2. Exportation Excel")
        excel_header.setStyleSheet("font-size: 14px; font-weight: bold; color: #2563EB;")
        excel_group_layout.addWidget(excel_header)
        
        excel_desc = QLabel("Exporte toutes vos données vers un fichier Excel (.xlsx) avec plusieurs feuilles.\nIdéal pour l'analyse, la comptabilité ou l'archivage.")
        excel_desc.setStyleSheet("color: #6B7280; font-size: 12px;")
        excel_desc.setWordWrap(True)
        excel_group_layout.addWidget(excel_desc)
        
        excel_btn = QPushButton("Exporter vers Excel")
        excel_btn.setMinimumHeight(42)
        excel_btn.setCursor(Qt.PointingHandCursor)
        excel_btn.setStyleSheet("""
            QPushButton {
                background: #2563EB; color: white; border: none;
                border-radius: 8px; padding: 10px 20px;
                font-weight: 600; font-size: 13px;
            }
            QPushButton:hover { background: #1D4ED8; }
        """)
        excel_btn.clicked.connect(self.export_to_excel)
        excel_group_layout.addWidget(excel_btn)
        
        backup_layout.addWidget(excel_group)
        
        # === Section 3: Delete Data (Danger Zone) ===
        danger_group = QFrame()
        danger_group.setStyleSheet("""
            QFrame {
                background: #FEF2F2; border: 1px solid #FECACA;
                border-radius: 10px; padding: 15px;
            }
        """)
        danger_layout = QVBoxLayout(danger_group)
        danger_layout.setSpacing(8)
        
        danger_header = QLabel("Zone Dangereuse - Suppression de Données")
        danger_header.setStyleSheet("font-size: 14px; font-weight: bold; color: #DC2626;")
        danger_layout.addWidget(danger_header)
        
        danger_desc = QLabel("Supprime les données de l'application. Cette action est IRRÉVERSIBLE.\nAssurez-vous d'avoir une sauvegarde récente avant de continuer.")
        danger_desc.setStyleSheet("color: #991B1B; font-size: 12px;")
        danger_desc.setWordWrap(True)
        danger_layout.addWidget(danger_desc)
        
        # Two delete buttons
        delete_btn_layout = QHBoxLayout()
        delete_btn_layout.setSpacing(10)
        
        del_data_btn = QPushButton("Supprimer les Données\n(Garder Utilisateurs)")
        del_data_btn.setMinimumHeight(50)
        del_data_btn.setCursor(Qt.PointingHandCursor)
        del_data_btn.setStyleSheet("""
            QPushButton {
                background: white; color: #DC2626;
                border: 2px solid #FCA5A5;
                border-radius: 8px; padding: 8px 14px;
                font-weight: 600; font-size: 12px;
            }
            QPushButton:hover { background: #FEF2F2; border: 2px solid #DC2626; }
        """)
        del_data_btn.clicked.connect(lambda: self.request_delete("data"))
        
        del_all_btn = QPushButton("Réinitialiser Totalement\n(Tout Supprimer)")
        del_all_btn.setMinimumHeight(50)
        del_all_btn.setCursor(Qt.PointingHandCursor)
        del_all_btn.setStyleSheet("""
            QPushButton {
                background: #DC2626; color: white;
                border: 2px solid #991B1B;
                border-radius: 8px; padding: 8px 14px;
                font-weight: 600; font-size: 12px;
            }
            QPushButton:hover { background: #991B1B; }
        """)
        del_all_btn.clicked.connect(lambda: self.request_delete("all"))
        
        delete_btn_layout.addWidget(del_data_btn)
        delete_btn_layout.addWidget(del_all_btn)
        danger_layout.addLayout(delete_btn_layout)
        
        backup_layout.addWidget(danger_group)
        backup_layout.addStretch()
        
        self.tabs.addTab(self.tab_backup, "Sauvegarde")

        # Tab 4: Matrix Configuration
        self.tab_matrix_config = QWidget()
        matrix_config_layout = QVBoxLayout(self.tab_matrix_config)
        self.matrix_config_widget = MatrixConfigWidget()
        matrix_config_layout.addWidget(self.matrix_config_widget)
        self.tabs.addTab(self.tab_matrix_config, "Configuration Matrice")

    def save_store_settings(self):
        SettingsModel.update_setting('store_name', self.store_name.text())
        SettingsModel.update_setting('store_phone', self.store_phone.text())
        SettingsModel.update_setting('store_address', self.store_address.text())
        QMessageBox.information(self, "Succès", "Paramètres de l'établissement enregistrés.")

    def load_users(self):
        users = SettingsModel.get_all_users()
        self.users_table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.users_table.setItem(row, 0, QTableWidgetItem(str(user['id'])))
            self.users_table.setItem(row, 1, QTableWidgetItem(user['username']))
            self.users_table.setItem(row, 2, QTableWidgetItem(user['role']))

    def add_user(self):
        username = self.user_username.text().strip()
        password = self.user_password.text()
        role = self.user_role.currentText()
        if not username or not password:
            QMessageBox.warning(self, "Erreur", "Nom d'utilisateur et mot de passe sont obligatoires.")
            return
        if SettingsModel.add_user(username, password, role):
            self.user_username.clear()
            self.user_password.clear()
            self.load_users()
            QMessageBox.information(self, "Succès", "Utilisateur ajouté avec succès.")

    def delete_user(self):
        selected = self.users_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un utilisateur à supprimer.")
            return
        user_id = self.users_table.item(selected[0].row(), 0).text()
        SettingsModel.delete_user(user_id)
        self.load_users()

    def create_backup(self):
        path = SettingsModel.backup_database()
        if path:
            QMessageBox.information(self, "Sauvegarde Réussie", f"Base de données sauvegardée avec succès à:\n{path}")
        else:
            QMessageBox.critical(self, "Erreur", "Échec de la sauvegarde.")

    def change_user_password(self):
        selected = self.users_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un utilisateur.")
            return
            
        row = selected[0].row()
        user_id = int(self.users_table.item(row, 0).text())
        username = self.users_table.item(row, 1).text()
        
        dialog = ChangePasswordDialog(username, self)
        if dialog.exec() == QDialog.Accepted:
            new_pass = dialog.new_pass_input.text()
            SettingsModel.update_password(user_id, new_pass)
            QMessageBox.information(self, "Succès", "Mot de passe modifié avec succès.")

    def create_db_backup(self):
        """Creates a timestamped SQLite database backup."""
        from datetime import datetime
        from config import DB_PATH, DATA_DIR
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"optiflow_backup_{timestamp}.db"
        default_path = f"{DATA_DIR}/{default_name}"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder la Base de Données", 
            default_path, "Database Files (*.db)"
        )
        
        if not file_path:
            return
        
        path = SettingsModel.backup_database_to_path(file_path)
        if path:
            QMessageBox.information(self, "Succès", 
                f"Base de données sauvegardée avec succès!\n\nEmplacement:\n{path}")
        else:
            QMessageBox.critical(self, "Erreur", "Échec de la sauvegarde.")
    
    def export_to_excel(self):
        """Exports all database tables to an Excel file."""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"optiflow_export_{timestamp}.xlsx"
        default_path = f"{DATA_DIR}/{default_name}"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter vers Excel",
            default_path, "Excel Files (*.xlsx)"
        )
        
        if not file_path:
            return
        
        # Show progress
        QMessageBox.information(self, "Exportation", 
            "Exportation en cours... Cela peut prendre un moment.")
        
        success = SettingsModel.export_to_excel(file_path)
        if success:
            reply = QMessageBox.information(self, "Succès",
                f"Données exportées avec succès!\n\nEmplacement:\n{file_path}\n\n"
                f"Le fichier contient des feuilles séparées pour chaque table.",
                QMessageBox.Open | QMessageBox.Ok)
            if reply == QMessageBox.Open:
                import os
                os.startfile(file_path)
        else:
            QMessageBox.critical(self, "Erreur", "Échec de l'exportation Excel.")
    
    def request_delete(self, delete_type):
        """Opens a password dialog to confirm deletion."""
        title = "Supprimer les Données" if delete_type == "data" else "Réinitialiser Totalement"
        warning = "Toutes les ventes, patients, stock seront supprimés." if delete_type == "data" else "TOUTES les données seront supprimées, y compris les utilisateurs. L'application redémarrera."
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{title}")
        dialog.setMinimumWidth(400)
        dialog_layout = QVBoxLayout(dialog)
        
        warning_label = QLabel(f"ATTENTION\n\n{warning}\n\nCette action est IRRÉVERSIBLE!")
        warning_label.setStyleSheet("color: #DC2626; font-weight: bold; font-size: 13px;")
        warning_label.setWordWrap(True)
        warning_label.setAlignment(Qt.AlignCenter)
        dialog_layout.addWidget(warning_label)
        
        form = QFormLayout()
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setPlaceholderText("Entrez votre mot de passe administrateur")
        password_input.setStyleSheet("padding: 8px; font-size: 14px;")
        form.addRow("Mot de passe:", password_input)
        dialog_layout.addLayout(form)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setObjectName("secondary")
        cancel_btn.clicked.connect(dialog.reject)
        
        confirm_btn = QPushButton("Confirmer la Suppression")
        confirm_btn.setStyleSheet("""
            QPushButton {
                background: #DC2626; color: white; border: none;
                border-radius: 6px; padding: 8px 16px;
                font-weight: 600; font-size: 13px;
            }
            QPushButton:hover { background: #991B1B; }
        """)
        confirm_btn.clicked.connect(dialog.accept)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(confirm_btn)
        dialog_layout.addLayout(btn_layout)
        
        if dialog.exec() == QDialog.Accepted:
            password = password_input.text()
            if not SettingsModel.verify_password(password):
                QMessageBox.critical(self, "Erreur", 
                    "Mot de passe incorrect. Suppression annulée.")
                return
            
            # Double confirmation
            reply = QMessageBox.question(self, "Dernière Confirmation",
                f"Êtes-vous absolument sûr de vouloir continuer?\n\n{warning}\n\n"
                f"Tapez 'OUI' dans la zone ci-dessous pour confirmer.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply != QMessageBox.Yes:
                return
            
            # Triple confirmation with typing
            text, ok = QInputDialog.getText(self, "Confirmation Finale",
                f"Pour confirmer, tapez 'SUPPRIMER' en majuscules:")
            
            if not ok or text != "SUPPRIMER":
                QMessageBox.information(self, "Annulé", "Suppression annulée.")
                return
            
            # Perform deletion
            if delete_type == "data":
                SettingsModel.delete_all_data()
                QMessageBox.information(self, "Succès", 
                    "Données supprimées avec succès.\nLes utilisateurs et paramètres ont été conservés.")
            else:
                SettingsModel.reset_database()
                QMessageBox.information(self, "Réinitialisé", 
                    "Base de données réinitialisée complètement.\nL'application va se fermer.")
                # Close the app so user can restart with fresh setup
                import sys
                sys.exit(0)