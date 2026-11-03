# views/settings_tab/matrix_config_widget.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QListWidget, QGroupBox, QMessageBox, 
                               QFileDialog, QInputDialog, QApplication)
from PySide6.QtCore import Qt
from models.lens_model import LensModel

# Hardcoded button styles
BTN_PRIMARY = """
    QPushButton {
        background: #2563EB; color: white; border: none;
        border-radius: 8px; padding: 8px 12px; font-weight: 600;
    }
    QPushButton:hover { background: #1D4ED8; }
"""
BTN_SECONDARY = """
    QPushButton {
        background: white; color: #111827; border: 1px solid #E5E7EB;
        border-radius: 8px; padding: 8px 12px; font-weight: 500;
    }
    QPushButton:hover { background: #F9FAFB; }
"""
BTN_DANGER = """
    QPushButton {
        color: #DC2626; background: transparent; border: none;
        font-weight: 500;
    }
    QPushButton:hover { color: #B91C1C; }
"""

class MatrixConfigWidget(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        
        info = QLabel("Ajoutez, modifiez ou supprimez des groupes (lignes) et traitements (colonnes).")
        info.setStyleSheet("color: #6B7280; margin-bottom: 10px;")
        main_layout.addWidget(info)

        columns_layout = QHBoxLayout()
        
        # === Groups Section ===
        group_box = QGroupBox("Groupes Optiques (Lignes)")
        group_layout = QVBoxLayout()
        self.group_list = QListWidget()
        self.load_groups()
        
        # Action buttons for Groups
        group_actions = QHBoxLayout()
        edit_group_btn = QPushButton("✏️ Modifier")
        edit_group_btn.setStyleSheet(BTN_SECONDARY)
        edit_group_btn.clicked.connect(self.modify_group)
        
        del_group_btn = QPushButton("🗑️ Supprimer")
        del_group_btn.setStyleSheet(BTN_DANGER)
        del_group_btn.clicked.connect(self.delete_group)
        
        group_actions.addWidget(edit_group_btn)
        group_actions.addWidget(del_group_btn)
        
        self.group_input = QLineEdit()
        self.group_input.setPlaceholderText("Ex: G 22")
        add_group_btn = QPushButton("＋ Ajouter Groupe")
        add_group_btn.setStyleSheet(BTN_PRIMARY)
        add_group_btn.clicked.connect(self.add_group)
        
        group_layout.addWidget(self.group_list)
        group_layout.addLayout(group_actions)
        group_layout.addWidget(self.group_input)
        group_layout.addWidget(add_group_btn)
        group_box.setLayout(group_layout)
        
        # === Treatments Section ===
        treat_box = QGroupBox("Traitements / Marques (Colonnes)")
        treat_layout = QVBoxLayout()
        self.treat_list = QListWidget()
        self.load_treatments()
        
        # Action buttons for Treatments
        treat_actions = QHBoxLayout()
        edit_treat_btn = QPushButton("✏️ Modifier")
        edit_treat_btn.setStyleSheet(BTN_SECONDARY)
        edit_treat_btn.clicked.connect(self.modify_treatment)
        
        del_treat_btn = QPushButton("🗑️ Supprimer")
        del_treat_btn.setStyleSheet(BTN_DANGER)
        del_treat_btn.clicked.connect(self.delete_treatment)
        
        treat_actions.addWidget(edit_treat_btn)
        treat_actions.addWidget(del_treat_btn)
        
        self.treat_input = QLineEdit()
        self.treat_input.setPlaceholderText("Ex: Essilor Crizal 1.6")
        add_treat_btn = QPushButton("＋ Ajouter Colonne")
        add_treat_btn.setStyleSheet(BTN_PRIMARY)
        add_treat_btn.clicked.connect(self.add_treatment)
        
        treat_layout.addWidget(self.treat_list)
        treat_layout.addLayout(treat_actions)
        treat_layout.addWidget(self.treat_input)
        treat_layout.addWidget(add_treat_btn)
        treat_box.setLayout(treat_layout)
        
        columns_layout.addWidget(group_box)
        columns_layout.addWidget(treat_box)
        main_layout.addLayout(columns_layout)
        
    def load_groups(self):
        self.group_list.clear()
        groups = LensModel.get_all_groups()
        self.group_list.addItems(groups)

    def load_treatments(self):
        self.treat_list.clear()
        treatments = LensModel.get_all_treatments()
        self.treat_list.addItems(treatments)

    def add_group(self):
        text = self.group_input.text().strip()
        if text:
            LensModel.add_group(text)
            self.group_input.clear()
            self.load_groups()
            self._set_dirty()
            QMessageBox.information(self, "Succès", "Groupe ajouté à la matrice.")
            
    def add_treatment(self):
        text = self.treat_input.text().strip()
        if text:
            LensModel.add_treatment(text)
            self.treat_input.clear()
            self.load_treatments()
            self._set_dirty()
            QMessageBox.information(self, "Succès", "Colonne ajoutée à la matrice.")

    def modify_group(self):
        selected = self.group_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un groupe à modifier.")
            return
        old_name = selected.text()
        new_name, ok = QInputDialog.getText(self, "Modifier le Groupe", "Nouveau nom:", text=old_name)
        if ok and new_name.strip():
            if LensModel.update_group(old_name, new_name):
                self.load_groups()
                self._set_dirty()
                QMessageBox.information(self, "Succès", "Groupe modifié avec succès.")

    def delete_group(self):
        selected = self.group_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un groupe à supprimer.")
            return
        group_name = selected.text()
        confirm = QMessageBox.question(self, "Confirmer", f"Supprimer le groupe '{group_name}' et tous ses prix associés?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            LensModel.delete_group(group_name)
            self.load_groups()
            self._set_dirty()
            QMessageBox.information(self, "Succès", "Groupe supprimé.")

    def modify_treatment(self):
        selected = self.treat_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une colonne à modifier.")
            return
        old_name = selected.text()
        new_name, ok = QInputDialog.getText(self, "Modifier la Colonne", "Nouveau nom:", text=old_name)
        if ok and new_name.strip():
            if LensModel.update_treatment(old_name, new_name):
                self.load_treatments()
                self._set_dirty()
                QMessageBox.information(self, "Succès", "Colonne modifiée avec succès.")

    def delete_treatment(self):
        selected = self.treat_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une colonne à supprimer.")
            return
        treat_name = selected.text()
        confirm = QMessageBox.question(self, "Confirmer", f"Supprimer la colonne '{treat_name}' et tous ses prix associés?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            LensModel.delete_treatment(treat_name)
            self.load_treatments()
            self._set_dirty()
            QMessageBox.information(self, "Succès", "Colonne supprimée.")

    def _set_dirty(self):
        """Tells the main app that the matrix structure has changed and needs reloading."""
        app = QApplication.instance()
        app.matrix_dirty = True