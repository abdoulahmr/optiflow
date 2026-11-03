# views/inventory_tab/inventory_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                               QComboBox, QDoubleSpinBox, QSpinBox, QDateEdit, 
                               QPushButton, QHBoxLayout, QMessageBox, QCheckBox)
from PySide6.QtCore import QDate
from models.inventory_model import InventoryModel, CONTACT_LENS_TYPES

class InventoryDialog(QDialog):
    def __init__(self, parent=None, item_id=None):
        super().__init__(parent)
        self.item_id = item_id
        self.setWindowTitle("Ajouter un Produit" if not item_id else "Modifier un Produit")
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(12)

        self.name_input = QLineEdit()
        
        # Main category dropdown (no individual contact lens types listed here)
        self.category_input = QComboBox()
        self.category_input.addItems([
            "Montures",
            "Lunettes de Soleil",
            "Lentilles",            # Single entry - reveals sub-filter
            "Produit de lentille",
            "Produits de nettoyage",
            "Accessoires"
        ])
        self.category_input.currentTextChanged.connect(self._on_category_changed)
        
        # Contact lens type sub-filter (hidden by default)
        self.cl_type_input = QComboBox()
        self.cl_type_input.addItems(CONTACT_LENS_TYPES)
        self.cl_type_input.setVisible(False)
        
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0, 999999)
        self.cost_input.setSuffix(" DA")

        self.retail_input = QDoubleSpinBox()
        self.retail_input.setRange(0, 999999)
        self.retail_input.setSuffix(" DA")

        self.stock_input = QSpinBox()
        self.stock_input.setRange(0, 99999)
        
        self.seuil_input = QSpinBox()
        self.seuil_input.setRange(0, 99999)
        self.seuil_input.setValue(5)

        self.perishable_check = QCheckBox("Produit périssable")
        self.perishable_check.toggled.connect(self.toggle_expiry)
        
        self.expiry_input = QDateEdit()
        self.expiry_input.setCalendarPopup(True)
        self.expiry_input.setDisplayFormat("yyyy-MM-dd")
        self.expiry_input.setDate(QDate.currentDate().addMonths(6))
        self.expiry_input.setEnabled(False)

        form.addRow("Nom du produit *:", self.name_input)
        form.addRow("Catégorie:", self.category_input)
        form.addRow("Type de Lentille:", self.cl_type_input)  # Hidden by default
        form.addRow("Prix d'Achat:", self.cost_input)
        form.addRow("Prix de Vente:", self.retail_input)
        form.addRow("Quantité en stock:", self.stock_input)
        form.addRow("Seuil d'alerte:", self.seuil_input)
        form.addRow("", self.perishable_check)
        form.addRow("Date d'expiration:", self.expiry_input)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setObjectName("secondary")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Enregistrer")
        save_btn.setObjectName("primary")
        save_btn.clicked.connect(self.save_item)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        # If editing, load existing data
        if self.item_id:
            item = InventoryModel.get_item_by_id(self.item_id)
            if item:
                self.name_input.setText(item['name'])
                
                # Handle contact lens category when editing
                if item['category'] in CONTACT_LENS_TYPES:
                    self.category_input.setCurrentText("Lentilles")
                    self.cl_type_input.setCurrentText(item['category'])
                else:
                    self.category_input.setCurrentText(item['category'])
                
                self.cost_input.setValue(item['cost_price'])
                self.retail_input.setValue(item['retail_price'])
                self.stock_input.setValue(item['stock_qty'])
                self.seuil_input.setValue(item['seuil'])
                if item['expiration_date']:
                    self.perishable_check.setChecked(True)
                    self.expiry_input.setDate(QDate.fromString(item['expiration_date'], "yyyy-MM-dd"))

    def _on_category_changed(self, category):
        """Shows/hides the contact lens type sub-filter based on category."""
        is_lentilles = (category == "Lentilles")
        self.cl_type_input.setVisible(is_lentilles)

    def toggle_expiry(self, checked):
        self.expiry_input.setEnabled(checked)

    def save_item(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Erreur", "Le nom du produit est obligatoire.")
            return
        
        # Determine final category
        category = self.category_input.currentText()
        if category == "Lentilles":
            category = self.cl_type_input.currentText()

        data = {
            'name': self.name_input.text().strip(),
            'category': category,
            'cost_price': self.cost_input.value(),
            'retail_price': self.retail_input.value(),
            'stock_qty': self.stock_input.value(),
            'seuil': self.seuil_input.value(),
            'expiration_date': self.expiry_input.date().toString("yyyy-MM-dd") if self.perishable_check.isChecked() else None
        }

        if self.item_id:
            InventoryModel.update_item(self.item_id, data)
        else:
            InventoryModel.add_item(data)
        self.accept()