# views/pos_tab/settle_debt_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                               QPushButton, QHBoxLayout, QMessageBox, QComboBox, 
                               QLabel)
from PySide6.QtCore import Qt
from models.pos_model import POSModel
from database.db_manager import db
from styles import PRIMARY, PRIMARY_HOVER, SUCCESS, BORDER, TEXT, DANGER

class SettleDebtDialog(QDialog):
    def __init__(self, order_id, parent=None):
        super().__init__(parent)
        self.order_id = order_id
        
        self.order = db.fetch_one("SELECT * FROM orders WHERE id=?", (order_id,))
        if not self.order:
            self.reject()
            return
        
        patient = db.fetch_one("SELECT nom, prenom FROM patients WHERE id=?", (self.order['patient_id'],))
        patient_name = f"{patient['nom']} {patient['prenom']}" if patient else "Inconnu"
        
        self.setWindowTitle(f"Solde - {self.order['client_id_text']}")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # 1. Header
        header = QLabel(f"{patient_name}  |  {self.order['client_id_text']}")
        header.setStyleSheet(f"color: {PRIMARY}; font-size: 13px; font-weight: bold;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        remaining = self.order['remaining_balance'] or 0
        
        # 2. Remaining balance
        remaining_label = QLabel(f"Reste à Payer: {remaining:,.2f} DA")
        remaining_label.setStyleSheet(f"color: {DANGER}; font-size: 20px; font-weight: bold;")
        remaining_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(remaining_label)

        # 3. Quick buttons
        quick_layout = QHBoxLayout()
        quick_layout.setSpacing(8)
        
        btn_full = QPushButton(f"Total ({remaining:,.0f} DA)")
        btn_full.setCursor(Qt.PointingHandCursor)
        btn_full.clicked.connect(lambda: self.deposit_input.setText(f"{remaining:.2f}"))
        btn_full.setStyleSheet(f"""
            QPushButton {{
                background: white; color: {TEXT};
                border: 2px solid {SUCCESS};
                border-radius: 8px; padding: 10px;
                font-weight: 600; font-size: 12px;
            }}
            QPushButton:hover {{ background: #F0FDF4; }}
        """)
        
        btn_half = QPushButton(f"Moitié ({remaining/2:,.0f} DA)")
        btn_half.setCursor(Qt.PointingHandCursor)
        btn_half.clicked.connect(lambda: self.deposit_input.setText(f"{remaining/2:.2f}"))
        btn_half.setStyleSheet(f"""
            QPushButton {{
                background: white; color: {TEXT};
                border: 2px solid {BORDER};
                border-radius: 8px; padding: 10px;
                font-weight: 600; font-size: 12px;
            }}
            QPushButton:hover {{ background: #F9FAFB; }}
        """)
        
        quick_layout.addWidget(btn_full)
        quick_layout.addWidget(btn_half)
        layout.addLayout(quick_layout)

        # 4. Manual input
        form = QFormLayout()
        form.setSpacing(8)
        
        self.deposit_input = QLineEdit()
        self.deposit_input.setText(f"{remaining:.2f}")
        self.deposit_input.setStyleSheet(f"""
            QLineEdit {{
                background: white; border: 2px solid {BORDER};
                border-radius: 8px; padding: 10px;
                font-size: 16px; font-weight: bold; color: {TEXT};
            }}
            QLineEdit:focus {{ border: 2px solid {PRIMARY}; }}
        """)
        self.deposit_input.textChanged.connect(self.calculate_new_balance)
        
        self.payment_method = QComboBox()
        self.payment_method.addItems(["Espèces", "CIB", "Chèque"])
        self.payment_method.setStyleSheet(f"""
            QComboBox {{
                background: white; border: 1px solid {BORDER};
                border-radius: 8px; padding: 8px;
                font-size: 14px;
            }}
        """)
        
        form.addRow("Montant:", self.deposit_input)
        form.addRow("Paiement:", self.payment_method)
        layout.addLayout(form)

        # 5. New balance preview
        self.new_balance_label = QLabel(f"Nouveau Reste: {remaining:,.2f} DA")
        self.new_balance_label.setStyleSheet(f"color: {DANGER}; font-weight: bold; font-size: 16px;")
        self.new_balance_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.new_balance_label)

        # 6. Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setObjectName("secondary")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        
        save_btn = QPushButton("✓ Enregistrer")
        save_btn.setMinimumHeight(40)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {PRIMARY}; color: white; border: none;
                border-radius: 8px; padding: 10px 20px;
                font-weight: 600; font-size: 14px;
            }}
            QPushButton:hover {{ background: {PRIMARY_HOVER}; }}
        """)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self.save_payment)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
        
        self.calculate_new_balance()

    def calculate_new_balance(self):
        try:
            amount = float(self.deposit_input.text()) if self.deposit_input.text() else 0.0
        except ValueError:
            amount = 0.0
        
        current_remaining = self.order['remaining_balance'] or 0
        new_remaining = current_remaining - amount
        
        if new_remaining <= 0.01:
            self.new_balance_label.setText("Sera Complètement Payé")
            self.new_balance_label.setStyleSheet(f"color: {SUCCESS}; font-weight: bold; font-size: 16px;")
        else:
            self.new_balance_label.setText(f"Nouveau Reste: {new_remaining:,.2f} DA")
            self.new_balance_label.setStyleSheet(f"color: {DANGER}; font-weight: bold; font-size: 16px;")

    def save_payment(self):
        try:
            amount = float(self.deposit_input.text()) if self.deposit_input.text() else 0.0
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Montant invalide.")
            return
        
        if amount <= 0:
            QMessageBox.warning(self, "Erreur", "Montant doit être supérieur à 0.")
            return
        
        success = POSModel.add_payment(self.order_id, amount, self.payment_method.currentText())
        if success:
            QMessageBox.information(self, "Succès", "Paiement enregistré!")
            self.accept()