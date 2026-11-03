# views/pos_tab/settlement_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                               QPushButton, QHBoxLayout, QMessageBox, QComboBox, 
                               QLabel, QFrame)
from PySide6.QtCore import Qt
from models.pos_model import POSModel
from styles import PRIMARY, PRIMARY_HOVER, SUCCESS, BORDER, TEXT
from models.patient_model import PatientModel
from views.components.receipt_view import ReceiptViewDialog

class SettlementDialog(QDialog):
    def __init__(self, patient_id, cart_items, parent=None):
        super().__init__(parent)
        self.patient_id = patient_id
        self.cart_items = cart_items
        self.total = sum(item['price'] - item.get('discount', 0) for item in cart_items)
        self.order_id = None
        self.client_id = None
        
        self.setWindowTitle("Règlement de la Commande")
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)  # Reduced padding
        layout.setSpacing(10)  # Reduced spacing

        # 1. Total Display (more compact)
        total_frame = QFrame()
        total_frame.setStyleSheet(f"""
            QFrame {{
                background: {PRIMARY}; border-radius: 10px;
                padding: 8px;
            }}
        """)
        total_layout = QVBoxLayout(total_frame)
        total_layout.setContentsMargins(0, 0, 0, 0)
        total_layout.setSpacing(2)
        
        total_label = QLabel("TOTAL À PAYER")
        total_label.setStyleSheet("color: #BFDBFE; font-size: 11px; font-weight: bold;")
        total_label.setAlignment(Qt.AlignCenter)
        
        self.total_value_label = QLabel(f"{self.total:,.2f} DA")
        self.total_value_label.setStyleSheet("color: white; font-size: 26px; font-weight: bold;")
        self.total_value_label.setAlignment(Qt.AlignCenter)
        
        total_layout.addWidget(total_label)
        total_layout.addWidget(self.total_value_label)
        layout.addWidget(total_frame)

        # 2. Payment Scenario Buttons
        scenario_label = QLabel("Mode de paiement:")
        scenario_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #374151;")
        layout.addWidget(scenario_label)
        
        # First row: Pay After | Pay Before
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(6)
        
        self.btn_pay_after = QPushButton("Payer Après\n(Crédit)")
        self.btn_pay_after.setToolTip("Le client ne paie rien maintenant. La totalité reste à payer.")
        self.btn_pay_after.setFixedHeight(44)  # Reduced from 60
        self.btn_pay_after.setCursor(Qt.PointingHandCursor)
        self.btn_pay_after.clicked.connect(lambda: self.set_payment_scenario("after"))
        self._style_scenario_button(self.btn_pay_after, False)
        
        self.btn_pay_before = QPushButton("Payer Avant\n(Total)")
        self.btn_pay_before.setToolTip("Le client paie la totalité maintenant.")
        self.btn_pay_before.setFixedHeight(44)  # Reduced from 60
        self.btn_pay_before.setCursor(Qt.PointingHandCursor)
        self.btn_pay_before.clicked.connect(lambda: self.set_payment_scenario("before"))
        self._style_scenario_button(self.btn_pay_before, False)
        
        row1_layout.addWidget(self.btn_pay_after)
        row1_layout.addWidget(self.btn_pay_before)
        layout.addLayout(row1_layout)
        
        # Second row: Pay in Two
        self.btn_pay_two = QPushButton("Payer en Deux Fois (Acompte)")
        self.btn_pay_two.setToolTip("Le client paie la moitié maintenant, le reste plus tard.")
        self.btn_pay_two.setFixedHeight(36)  # Reduced from 50
        self.btn_pay_two.setCursor(Qt.PointingHandCursor)
        self.btn_pay_two.clicked.connect(lambda: self.set_payment_scenario("two"))
        self._style_scenario_button(self.btn_pay_two, False)
        layout.addWidget(self.btn_pay_two)

        # 3. Manual Deposit Input
        form = QFormLayout()
        form.setSpacing(6)  # Reduced
        form.setContentsMargins(0, 0, 0, 0)
        
        self.deposit_input = QLineEdit()
        self.deposit_input.setText(f"{self.total:.2f}")
        self.deposit_input.setStyleSheet(f"""
            QLineEdit {{
                background: white; border: 2px solid {BORDER};
                border-radius: 6px; padding: 6px;
                font-size: 16px; font-weight: bold; color: {TEXT};
            }}
            QLineEdit:focus {{ border: 2px solid {PRIMARY}; }}
        """)
        self.deposit_input.textChanged.connect(self.calculate_balance)
        
        self.payment_method = QComboBox()
        self.payment_method.addItems(["Espèces", "CIB", "Chèque"])
        self.payment_method.setStyleSheet(f"""
            QComboBox {{
                background: white; border: 1px solid {BORDER};
                border-radius: 6px; padding: 6px;
                font-size: 13px;
            }}
        """)
        
        form.addRow("Montant Reçu:", self.deposit_input)
        form.addRow("Paiement:", self.payment_method)
        layout.addLayout(form)

        # 4. Balance Display (more compact)
        self.balance_frame = QFrame()
        self.balance_frame.setStyleSheet(f"""
            QFrame {{
                background: #FEF2F2; border: 1px solid #FECACA;
                border-radius: 6px; padding: 6px;
            }}
        """)
        balance_layout = QVBoxLayout(self.balance_frame)
        balance_layout.setContentsMargins(0, 0, 0, 0)
        balance_layout.setSpacing(2)
        
        self.balance_label = QLabel("Reste à Payer: 0.00 DA")
        self.balance_label.setStyleSheet(f"color: #DC2626; font-weight: bold; font-size: 15px;")
        self.balance_label.setAlignment(Qt.AlignCenter)
        balance_layout.addWidget(self.balance_label)
        
        self.status_hint = QLabel("Statut: Livré (Payé)")
        self.status_hint.setStyleSheet("color: #6B7280; font-size: 11px;")
        self.status_hint.setAlignment(Qt.AlignCenter)
        balance_layout.addWidget(self.status_hint)
        
        layout.addWidget(self.balance_frame)

        # 5. Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setObjectName("secondary")
        cancel_btn.setFixedHeight(38)  # Reduced from 45
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("✓ Finaliser la Vente")
        save_btn.setFixedHeight(38)  # Reduced from 45
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {PRIMARY}; color: white; border: none;
                border-radius: 6px; padding: 6px 18px;
                font-weight: 600; font-size: 13px;
            }}
            QPushButton:hover {{ background: {PRIMARY_HOVER}; }}
        """)
        save_btn.clicked.connect(self.finalize_sale)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
        
        # Default scenario: Pay Before (full payment)
        self.set_payment_scenario("before")

    def _style_scenario_button(self, btn, selected):
        """Applies selected/unselected styling to scenario buttons."""
        if selected:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {PRIMARY}; color: white;
                    border: 2px solid {PRIMARY_HOVER};
                    border-radius: 6px;
                    font-weight: bold; font-size: 12px;
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: white; color: {TEXT};
                    border: 1px solid {BORDER};
                    border-radius: 6px;
                    font-weight: 500; font-size: 12px;
                }}
                QPushButton:hover {{
                    background: #F9FAFB; border: 1px solid {PRIMARY};
                }}
            """)

    def set_payment_scenario(self, scenario):
        """Sets the deposit based on the selected scenario."""
        self._style_scenario_button(self.btn_pay_after, False)
        self._style_scenario_button(self.btn_pay_before, False)
        self._style_scenario_button(self.btn_pay_two, False)
        
        if scenario == "after":
            self._style_scenario_button(self.btn_pay_after, True)
            self.deposit_input.setText("0.00")
            
        elif scenario == "before":
            self._style_scenario_button(self.btn_pay_before, True)
            self.deposit_input.setText(f"{self.total:.2f}")
            
        elif scenario == "two":
            self._style_scenario_button(self.btn_pay_two, True)
            half = self.total / 2
            self.deposit_input.setText(f"{half:.2f}")

    def calculate_balance(self):
        try:
            deposit = float(self.deposit_input.text()) if self.deposit_input.text() else 0.0
        except ValueError:
            deposit = 0.0
            
        balance = self.total - deposit
        
        if balance > 0.01:
            self.balance_label.setText(f"Reste à Payer: {balance:,.2f} DA")
            self.balance_label.setStyleSheet(f"color: #DC2626; font-weight: bold; font-size: 15px;")
            self.balance_frame.setStyleSheet("""
                QFrame { background: #FEF2F2; border: 1px solid #FECACA; border-radius: 6px; padding: 6px; }
            """)
            self.status_hint.setText("Statut: En cours (Crédit)")
            self.status_hint.setStyleSheet("color: #D97706; font-size: 11px; font-weight: bold;")
            
        elif balance < -0.01:
            self.balance_label.setText(f"Rendu (Monnaie): {abs(balance):,.2f} DA")
            self.balance_label.setStyleSheet(f"color: {SUCCESS}; font-weight: bold; font-size: 15px;")
            self.balance_frame.setStyleSheet(f"""
                QFrame {{ background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 6px; padding: 6px; }}
            """)
            self.status_hint.setText("Statut: Livré (Payé)")
            self.status_hint.setStyleSheet(f"color: {SUCCESS}; font-size: 11px; font-weight: bold;")
            
        else:
            self.balance_label.setText("Payé en Totalité")
            self.balance_label.setStyleSheet(f"color: {SUCCESS}; font-weight: bold; font-size: 15px;")
            self.balance_frame.setStyleSheet(f"""
                QFrame {{ background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 6px; padding: 6px; }}
            """)
            self.status_hint.setText("Statut: Livré (Payé)")
            self.status_hint.setStyleSheet(f"color: {SUCCESS}; font-size: 11px; font-weight: bold;")

    def finalize_sale(self):
        if not self.patient_id:
            QMessageBox.warning(self, "Erreur", "Aucun patient sélectionné.")
            return
            
        try:
            deposit = float(self.deposit_input.text()) if self.deposit_input.text() else 0.0
        except ValueError:
            deposit = 0.0
            
        balance = self.total - deposit
        
        if balance > 0.01:
            status = "En cours"
        else:
            status = "Livré"
        
        order_id, client_id = POSModel.create_order(
            self.patient_id, 
            self.cart_items, 
            deposit, 
            self.payment_method.currentText(),
            status
        )
        
        if order_id:
            self.order_id = order_id
            self.client_id = client_id
            
            # === NEW: Show the receipt preview after saving ===
            try:
                patient_data = PatientModel.get_patient(self.patient_id)
                order_data = {
                    'client_id': client_id,
                    'total_payable': self.total,
                    'deposit_received': deposit,
                    'remaining_balance': balance,
                    'payment_method': self.payment_method.currentText(),
                    'status': status
                }
                
                # Filter out any negative-price entries (e.g. payment records)
                cart_for_receipt = [
                    item for item in self.cart_items 
                    if item.get('price', 0) >= 0
                ]
                
                receipt_dialog = ReceiptViewDialog(order_data, patient_data, cart_for_receipt, self)
                receipt_dialog.exec()
            except Exception as e:
                print(f"Receipt preview error: {e}")
                QMessageBox.information(self, "Succès", 
                    f"Vente finalisée avec succès!\nID Ticket: {client_id}")
            
            self.accept()