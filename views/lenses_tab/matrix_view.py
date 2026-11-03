# views/lenses_tab/matrix_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTabWidget, QButtonGroup, QRadioButton, 
                               QMessageBox, QFileDialog, QApplication)
from PySide6.QtCore import Qt
import csv
from views.components.lens_matrix_tab import LensMatrixTab
from models.lens_model import LensModel
from database.db_manager import db

class MatrixView(QWidget):
    def __init__(self, user=None):
        super().__init__()
        self.user = user
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # 1. Header
        title = QLabel("Matrice des Prix des Verres")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Configurez les prix de vente et d'achat par groupe optique")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        # 2. Action Bar
        action_bar = QHBoxLayout()
        
        # Price Toggle (Styled as Buttons)
        self.price_group = QButtonGroup(self)
        self.price_group.setExclusive(True)
        
        # Radio Button Style
        toggle_style = """
            QRadioButton {
                background: white;
                color: #6B7280;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QRadioButton::indicator {
                width: 0px;
                height: 0px;
            }
            QRadioButton:checked {
                background: #2563EB;
                color: white;
                border: 1px solid #2563EB;
            }
        """
        
        self.radio_retail = QRadioButton("Prix de Vente")
        self.radio_retail.setChecked(True)
        self.radio_retail.setStyleSheet(toggle_style)
        self.radio_retail.setCursor(Qt.PointingHandCursor)
        
        self.radio_cost = QRadioButton("Prix d'Achat")
        self.radio_cost.setStyleSheet(toggle_style)
        self.radio_cost.setCursor(Qt.PointingHandCursor)
        
        self.price_group.addButton(self.radio_retail)
        self.price_group.addButton(self.radio_cost)
        self.radio_retail.toggled.connect(self.toggle_price_mode)
        
        action_bar.addWidget(self.radio_retail)
        action_bar.addWidget(self.radio_cost)
        action_bar.addStretch()
        
        # Edit / Save Buttons
        self.edit_btn = QPushButton("Modifier")
        self.edit_btn.setObjectName("secondary")
        self.edit_btn.clicked.connect(self.toggle_edit_mode)
        
        self.save_btn = QPushButton("Enregistrer")
        self.save_btn.setObjectName("primary")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #2563EB; color: white; border: none;
                border-radius: 8px; padding: 10px 16px; font-weight: 600; font-size: 14px;
            }
            QPushButton:hover { background: #1D4ED8; }
        """)
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_matrix)
        
        # PRIVILEGE CHECK: Hide buttons if not admin
        if not self.user or self.user['role'] != 'Administrateur':
            self.edit_btn.setVisible(False)
            self.save_btn.setVisible(False)
        
        action_bar.addWidget(self.edit_btn)
        action_bar.addWidget(self.save_btn)
        layout.addLayout(action_bar)

        # 3. Tabs
        self.tabs = QTabWidget()
        self.tab_transparent = LensMatrixTab("Transparent")
        self.tab_photochromic = LensMatrixTab("Photochromique")
        self.tab_special = LensMatrixTab("Speciale")
        self.tabs.addTab(self.tab_transparent, "Verre Transparent")
        self.tabs.addTab(self.tab_photochromic, "Verre Photochromique")
        self.tabs.addTab(self.tab_special, "Verres Spéciale")
        layout.addWidget(self.tabs)

    def toggle_price_mode(self):
        mode = "retail" if self.radio_retail.isChecked() else "cost"
        self.tab_transparent.set_price_mode(mode)
        self.tab_photochromic.set_price_mode(mode)
        self.tab_special.set_price_mode(mode)
        
        # If we were in edit mode, cancel it because the grid rebuilt
        if self.edit_btn.text() == "Annuler":
            self.toggle_edit_mode()

    def toggle_edit_mode(self):
        is_editing = self.edit_btn.text() == "Modifier"
        current_tab = self.tabs.currentWidget()
        current_tab.set_edit_mode(is_editing)
        
        if is_editing:
            self.edit_btn.setText("Annuler")
            self.save_btn.setEnabled(True)
        else:
            self.edit_btn.setText("Modifier")
            self.save_btn.setEnabled(False)
            current_tab.load_data() # Reload to discard unsaved changes

    def save_matrix(self):
        current_tab = self.tabs.currentWidget()
        data = current_tab.get_changed_data()
        LensModel.save_matrix_batch(data)
        
        # Exit edit mode
        self.edit_btn.setText("Modifier")
        self.save_btn.setEnabled(False)
        current_tab.set_edit_mode(False)
        QMessageBox.information(self, "Succès", "Prix enregistrés avec succès.")
        
        # Tell the app the catalogue needs refreshing
        app = QApplication.instance()
        app.catalogue_dirty = True

    def reload_data(self):
        """Forces the matrix to fetch new groups/treatments and redraw."""
        self.tab_transparent.load_data()
        self.tab_photochromic.load_data()
        self.tab_special.load_data()