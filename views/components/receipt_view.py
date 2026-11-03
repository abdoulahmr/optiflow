# views/components/receipt_view.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTextBrowser, QPushButton, 
                               QHBoxLayout, QLabel)
from PySide6.QtCore import Qt
from utils.receipt_printer import ReceiptPrinter

class ReceiptViewDialog(QDialog):
    def __init__(self, order_data, patient_data, cart_items, parent=None):
        super().__init__(parent)
        self.order_data = order_data
        self.patient_data = patient_data
        self.cart_items = cart_items
        
        self.setWindowTitle("Aperçu du Ticket de Caisse (A4)")
        self.setMinimumWidth(850)  # Changed to minimumWidth to be responsive
        self.setMinimumHeight(600) # Added height

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Title
        title = QLabel("Aperçu du Document (A4 Demi-Page)")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        layout.addWidget(title)

        # HTML Preview Browser
        self.browser = QTextBrowser()
        html = ReceiptPrinter.generate_html(order_data, patient_data, cart_items)
        self.browser.setHtml(html)
        layout.addWidget(self.browser)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        close_btn = QPushButton("Fermer")
        close_btn.setObjectName("secondary")
        close_btn.clicked.connect(self.reject)
        
        print_btn = QPushButton("🖨️ Imprimer")
        print_btn.setMinimumHeight(40)
        # Hardcode the hex codes to prevent it from turning white
        print_btn.setStyleSheet("""
            QPushButton {
                background: #2563EB;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 11px 18px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #1D4ED8;
            }
        """)
        print_btn.setCursor(Qt.PointingHandCursor)
        print_btn.clicked.connect(self.print_document)
        
        btn_layout.addWidget(close_btn)
        btn_layout.addWidget(print_btn)
        layout.addLayout(btn_layout)

    def print_document(self):
        """Triggers the actual physical printer dialog."""
        ReceiptPrinter.print_receipt(self.order_data, self.patient_data, self.cart_items)