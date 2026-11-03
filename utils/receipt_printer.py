# utils/receipt_printer.py
from PySide6.QtGui import QTextDocument, QPageSize
from PySide6.QtCore import QSizeF
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from datetime import datetime

class ReceiptPrinter:
    @staticmethod
    def generate_html(order_data, patient_data, cart_items):
        """Generates the HTML string for the A4 receipt."""
        # A4 width is ~794 pixels at 96dpi. We use 100% and padding for flexibility.
        return f"""
        <html><head><style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; width: 100%; padding: 20px; box-sizing: border-box; }}
            h1 {{ font-size: 28px; text-align: center; margin: 5px 0; }}
            h2 {{ font-size: 18px; text-align: center; margin: 0 0 20px 0; color: #555; }}
            .center {{ text-align: center; }}
            .right {{ text-align: right; }}
            .bold {{ font-weight: bold; }}
            hr {{ border-top: 2px solid #111; margin: 15px 0; }}
            table {{ width: 100%; border-collapse: collapse; font-size: 16px; }}
            td {{ padding: 8px 0; vertical-align: top; }}
            .totals-table td {{ padding: 5px 0; }}
        </style></head><body>
            
            <h1>OptiFlow Store</h1>
            <h2>Votre Opticien de Confiance</h2>
            <p class="center">
                Tel: 05 50 50 50 50<br>
                Adresse: 12 Rue Centrale, Alger<br>
                Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            </p>
            <hr>
            
            <table>
                <tr>
                    <td style="width: 50%;">
                        <b>Client:</b> {patient_data['nom']} {patient_data['prenom']}<br>
                        <b>Tel:</b> {patient_data['phone'] or 'N/A'}
                    </td>
                    <td class="right" style="width: 50%;">
                        <b>ID Client:</b> {order_data['client_id']}<br>
                        <b>Statut:</b> {order_data['status']}
                    </td>
                </tr>
            </table>
            <hr>
            
            <table>
                <tr class="bold" style="border-bottom: 2px solid #111;">
                    <td>Article & Description</td>
                    <td class="right">Prix (DA)</td>
                </tr>
        """ + "".join([
            f"""
                <tr>
                    <td>{item['type']}<br><i>{item['description']}</i></td>
                    <td class="right">{item['price'] - item.get('discount', 0.0):.2f}</td>
                </tr>
            """ + (f"""<tr><td class="right">(Remise: -{item.get('discount', 0.0):.2f})</td><td></td></tr>""" if item.get('discount', 0.0) > 0 else "")
            for item in cart_items
        ]) + f"""
            </table>
            <hr>
            
            <table class="totals-table" style="margin-left: auto; width: 50%;">
                <tr class="bold"><td>TOTAL A PAYER:</td><td class="right">{order_data['total_payable']:.2f} DA</td></tr>
                <tr><td>Versement Reçu:</td><td class="right">{order_data['deposit_received']:.2f} DA</td></tr>
                <tr class="bold" style="font-size: 20px; color: #DC2626;"><td>RESTE A PAYER:</td><td class="right">{order_data['remaining_balance']:.2f} DA</td></tr>
            </table>
            <hr>
            
            <p class="center">
                Mode de Paiement: {order_data['payment_method']}
            </p>
            <hr>
            
            <p class="center" style="font-size: 14px; margin-top: 30px;">
                Merci de votre confiance !<br>
                شكراً على ثقتكم<br><br>
                * Les échanges se font sous 7 jours avec le ticket.*
            </p>
            
        </body></html>
        """

    @staticmethod
    def print_receipt(order_data, patient_data, cart_items):
        """Sends the HTML to the physical printer."""
        html = ReceiptPrinter.generate_html(order_data, patient_data, cart_items)
        
        printer = QPrinter(QPrinter.HighResolution)
        
        # A4 Width = 210mm, A4/2 Height = 148.5mm
        page_size = QPageSize(QSizeF(210, 148.5), QPageSize.Unit.Millimeter)
        printer.setPageSize(page_size)
        printer.setColorMode(QPrinter.ColorMode.GrayScale)
        
        dialog = QPrintDialog(printer)
        if dialog.exec() == QPrintDialog.Accepted:
            doc = QTextDocument()
            doc.setHtml(html)
            # Set the document page size so it formats correctly for the printer
            doc.setPageSize(printer.pageRect(QPrinter.Unit.Point).size())
            doc.print_(printer)