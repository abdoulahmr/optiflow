# views/patients_tab/patient_profile_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTabWidget, QWidget, 
                               QFormLayout, QLineEdit, QDateEdit, QLabel, 
                               QPushButton, QHBoxLayout, QMessageBox, QFrame,
                               QScrollArea, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QAbstractItemView, QSplitter,
                               QTreeWidget, QTreeWidgetItem)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor
from models.patient_model import PatientModel
from models.prescription_model import PrescriptionModel
from models.contact_lens_model import ContactLensModel
from models.finance_model import FinanceModel
from views.components.refraction_grid import RefractionGrid
from views.components.contact_lens_grid import ContactLensGrid
from database.db_manager import db


class PatientProfileDialog(QDialog):
    def __init__(self, patient_id, parent=None):
        super().__init__(parent)
        self.patient_id = patient_id
        self.patient_data = PatientModel.get_patient(patient_id)
        
        self.setWindowTitle(f"Fiche Client - {self.patient_data['nom']} {self.patient_data['prenom']}")
        self.setMinimumWidth(750)
        self.setMinimumHeight(650)

        # Main layout for the dialog
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area to make the whole dialog scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")
        
        # Container widget for all content
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # ==========================================
        # TAB 1: Personal Info
        # ==========================================
        self.info_tab = QWidget()
        info_layout = QFormLayout(self.info_tab)
        
        self.nom_input = QLineEdit(self.patient_data['nom'])
        self.prenom_input = QLineEdit(self.patient_data['prenom'])
        self.phone_input = QLineEdit(self.patient_data['phone'])
        self.address_input = QLineEdit(self.patient_data['address'] or "")
        
        info_layout.addRow("Nom:", self.nom_input)
        info_layout.addRow("Prénom:", self.prenom_input)
        info_layout.addRow("Téléphone:", self.phone_input)
        info_layout.addRow("Adresse:", self.address_input)
        self.tabs.addTab(self.info_tab, "Informations")

        # ==========================================
        # TAB 2: Correction Optique (Grid + History Table)
        # ==========================================
        self.optical_tab = QWidget()
        optical_layout = QVBoxLayout(self.optical_tab)
        
        # Exam Date
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date d'examen:"))
        self.exam_date = QDateEdit()
        self.exam_date.setCalendarPopup(True)
        self.exam_date.setDate(QDate.currentDate())
        self.exam_date.setDisplayFormat("yyyy-MM-dd")
        date_layout.addWidget(self.exam_date)
        date_layout.addStretch()
        optical_layout.addLayout(date_layout)

        # Refraction Grids (Active prescription)
        self.vl_grid = RefractionGrid("Vision de Loin (VL)")
        self.vp_grid = RefractionGrid("Vision de Près (VP)")
        optical_layout.addWidget(self.vl_grid)
        optical_layout.addWidget(self.vp_grid)
        
        # History Tree (Collapsible by date)
        history_label = QLabel("Historique des Corrections")
        history_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2563EB; margin-top: 10px;")
        optical_layout.addWidget(history_label)
        
        self.rx_history_tree = QTreeWidget()
        self.rx_history_tree.setHeaderLabels([
            "Date / Vision", "SPH OD", "CYL OD", "AXE OD", 
            "SPH OG", "CYL OG", "AXE OG", "ADD"
        ])
        self.rx_history_tree.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.rx_history_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.rx_history_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 8):
            self.rx_history_tree.header().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.rx_history_tree.setRootIsDecorated(True)
        self.rx_history_tree.setAnimated(True)
        self.rx_history_tree.setUniformRowHeights(True)
        self.rx_history_tree.setMinimumHeight(200)
        optical_layout.addWidget(self.rx_history_tree)
        self.tabs.addTab(self.optical_tab, "Correction Optique")

        # ==========================================
        # TAB 3: Lentilles de Contact (Grid + History Table)
        # ==========================================
        self.lens_tab = QWidget()
        lens_layout = QVBoxLayout(self.lens_tab)
        
        self.contact_lens_grid = ContactLensGrid()
        lens_layout.addWidget(self.contact_lens_grid)
        
        # History Table
        cl_history_label = QLabel("Historique des Lentilles de Contact")
        cl_history_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #0D9488; margin-top: 10px;")
        lens_layout.addWidget(cl_history_label)
        
        self.cl_history_table = QTableWidget()
        self.cl_history_table.setColumnCount(8)
        self.cl_history_table.setHorizontalHeaderLabels([
            "Date", "Type", "Marque", "Couleur",
            "OD (SPH/CYL/BC)", "OG (SPH/CYL/BC)", "Diamètre", "Observations"
        ])
        self.cl_history_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.cl_history_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.cl_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.cl_history_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Stretch)
        self.cl_history_table.verticalHeader().setVisible(False)
        self.cl_history_table.setMinimumHeight(150)
        lens_layout.addWidget(self.cl_history_table)
        
        self.tabs.addTab(self.lens_tab, "Lentilles de Contact")

        # ==========================================
        # TAB 4: Historique des Montures (Frames History)
        # ==========================================
        self.frames_tab = QWidget()
        frames_layout = QVBoxLayout(self.frames_tab)
        
        frames_label = QLabel("Historique des Montures & Accessoires")
        frames_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #7C3AED;")
        frames_layout.addWidget(frames_label)
        
        subtitle = QLabel("Toutes les montures et accessoires achetés par ce client")
        subtitle.setStyleSheet("color: #6B7280; font-size: 13px; margin-bottom: 10px;")
        frames_layout.addWidget(subtitle)
        
        self.frames_table = QTableWidget()
        self.frames_table.setColumnCount(7)
        self.frames_table.setHorizontalHeaderLabels([
            "Date", "ID Ticket", "Article", "Prix (DA)", "Remise (DA)", "Prix Final (DA)"
        ])
        self.frames_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.frames_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.frames_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.frames_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.frames_table.verticalHeader().setVisible(False)
        frames_layout.addWidget(self.frames_table)
        
        # Summary card at bottom
        self.frames_summary = QLabel("")
        self.frames_summary.setStyleSheet("""
            QLabel {
                background: #F5F3FF; color: #7C3AED;
                border: 1px solid #DDD6FE; border-radius: 8px;
                padding: 15px; font-size: 14px; font-weight: bold;
            }
        """)
        self.frames_summary.setAlignment(Qt.AlignCenter)
        frames_layout.addWidget(self.frames_summary)
        
        self.tabs.addTab(self.frames_tab, "Historique Montures")

        # Save Button (OUTSIDE the scroll area, always visible at bottom)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        save_btn = QPushButton("Enregistrer les modifications")
        save_btn.setObjectName("primary")
        save_btn.setMinimumHeight(40)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #2563EB; color: white; border: none;
                border-radius: 8px; padding: 12px 24px;
                font-weight: 600; font-size: 14px;
            }
            QPushButton:hover { background: #1D4ED8; }
        """)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self.save_all)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
        
        # Set the container as the scroll area's widget
        scroll.setWidget(container)
        
        # Add the scroll area to the main layout
        main_layout.addWidget(scroll)

        # Load all data
        self.load_prescription()
        self.load_contact_lenses()
        self.load_frames_history()

    def fmt_rx(self, val):
        """Format optical values with sign."""
        if val is None: return "0.00"
        return f"{val:+.2f}" if val != 0 else "0.00"

    def load_prescription(self):
        """Loads active prescription into grid, and all history into tree."""
        rx = PrescriptionModel.get_prescription(self.patient_id)
        if rx:
            self.exam_date.setDate(QDate.fromString(rx['exam_date'], "yyyy-MM-dd"))
            self.vl_grid.set_data(rx)
            self.vp_grid.sph_od.setValue(rx['vp_sph_od'] or 0.0)
            self.vp_grid.sph_og.setValue(rx['vp_sph_og'] or 0.0)
        
        # Load history tree
        self.rx_history_tree.clear()
        all_rx = PatientModel.get_all_prescriptions(self.patient_id)
        
        bold_font = QFont()
        bold_font.setBold(True)
        
        for rx in all_rx:
            date_str = rx['exam_date'] or "Date inconnue"
            
            # Parent item: the date
            parent = QTreeWidgetItem([f"{date_str}", "", "", "", "", "", "", ""])
            parent.setFont(0, bold_font)
            parent.setForeground(0, QColor("#2563EB"))
            parent.setBackground(0, QColor("#EFF6FF"))
            parent.setBackground(1, QColor("#EFF6FF"))
            parent.setBackground(2, QColor("#EFF6FF"))
            parent.setBackground(3, QColor("#EFF6FF"))
            parent.setBackground(4, QColor("#EFF6FF"))
            parent.setBackground(5, QColor("#EFF6FF"))
            parent.setBackground(6, QColor("#EFF6FF"))
            parent.setBackground(7, QColor("#EFF6FF"))
            
            # Child 1: VL (Vision de Loin)
            vl_item = QTreeWidgetItem([
                "VL (Vision de Loin)",
                self.fmt_rx(rx['vl_sph_od']),
                self.fmt_rx(rx['vl_cyl_od']),
                f"{rx['vl_axe_od'] or 0}°",
                self.fmt_rx(rx['vl_sph_og']),
                self.fmt_rx(rx['vl_cyl_og']),
                f"{rx['vl_axe_og'] or 0}°",
                self.fmt_rx(rx['vl_add_od'])
            ])
            vl_item.setForeground(0, QColor("#2563EB"))
            
            # Child 2: VP (Vision de Près)
            vp_item = QTreeWidgetItem([
                "VP (Vision de Près)",
                self.fmt_rx(rx['vp_sph_od']),
                self.fmt_rx(rx['vp_cyl_od']),
                f"{rx['vp_axe_od'] or 0}°",
                self.fmt_rx(rx['vp_sph_og']),
                self.fmt_rx(rx['vp_cyl_og']),
                f"{rx['vp_axe_og'] or 0}°",
                self.fmt_rx(rx['vp_add_od'])
            ])
            vp_item.setForeground(0, QColor("#0D9488"))
            
            parent.addChild(vl_item)
            parent.addChild(vp_item)
            
            # Auto-expand the most recent (first) one
            if rx == all_rx[0]:
                parent.setExpanded(True)
            else:
                parent.setExpanded(False)
            
            self.rx_history_tree.addTopLevelItem(parent)
        
        # If no history, show placeholder
        if not all_rx:
            empty = QTreeWidgetItem(["Aucune correction enregistrée", "", "", "", "", "", "", ""])
            empty.setForeground(0, QColor("#9CA3AF"))
            self.rx_history_tree.addTopLevelItem(empty)

    def load_contact_lenses(self):
        """Loads active contact lens fitting into grid, all history into table."""
        cl = ContactLensModel.get_lenses(self.patient_id)
        if cl:
            self.contact_lens_grid.set_data(cl)
        
        # Load history table
        all_cl = PatientModel.get_all_contact_lenses(self.patient_id)
        self.cl_history_table.setRowCount(len(all_cl))
        for row, cl in enumerate(all_cl):
            self.cl_history_table.setItem(row, 0, QTableWidgetItem(cl['fitting_date'] or "N/A"))
            self.cl_history_table.setItem(row, 1, QTableWidgetItem(cl['type'] or "N/A"))
            self.cl_history_table.setItem(row, 2, QTableWidgetItem(cl['marque'] or "N/A"))
            self.cl_history_table.setItem(row, 3, QTableWidgetItem(cl['color'] or "N/A"))
            
            od_str = f"SPH {self.fmt_rx(cl['od_sph'])} / CYL {self.fmt_rx(cl['od_cyl'])} / BC {cl['od_rayon_bc'] or 'N/A'}"
            og_str = f"SPH {self.fmt_rx(cl['og_sph'])} / CYL {self.fmt_rx(cl['og_cyl'])} / BC {cl['og_rayon_bc'] or 'N/A'}"
            
            self.cl_history_table.setItem(row, 4, QTableWidgetItem(od_str))
            self.cl_history_table.setItem(row, 5, QTableWidgetItem(og_str))
            self.cl_history_table.setItem(row, 6, QTableWidgetItem(f"{cl['od_diametre'] or 'N/A'}"))
            self.cl_history_table.setItem(row, 7, QTableWidgetItem(cl['observations'] or ""))

    def load_frames_history(self):
        """Loads all frame/accessory purchases for this patient."""
        query = """
            SELECT o.id, o.created_at, o.client_id_text, oi.description, oi.price, oi.discount, o.status
            FROM orders o
            JOIN order_items oi ON oi.order_id = o.id
            WHERE o.patient_id = ? 
              AND oi.item_type IN ('Montures', 'Accessoires', 'Produits de nettoyage', 'Produit de lentille')
            ORDER BY o.created_at DESC
        """
        frames = db.fetch_all(query, (self.patient_id,))
        
        self.frames_table.setRowCount(len(frames))
        total_spent = 0.0
        items_count = len(frames)
        
        for row, item in enumerate(frames):
            date_str = item['created_at'][:10] if item['created_at'] else "N/A"
            final_price = item['price'] - (item['discount'] or 0)
            total_spent += final_price
            
            self.frames_table.setItem(row, 0, QTableWidgetItem(date_str))
            self.frames_table.setItem(row, 1, QTableWidgetItem(item['client_id_text'] or "N/A"))
            self.frames_table.setItem(row, 2, QTableWidgetItem(item['description']))
            self.frames_table.setItem(row, 3, QTableWidgetItem(f"{item['price']:.2f}"))
            self.frames_table.setItem(row, 4, QTableWidgetItem(f"{item['discount'] or 0:.2f}"))
            self.frames_table.setItem(row, 5, QTableWidgetItem(f"{final_price:.2f}"))
            
            status_item = QTableWidgetItem(item['status'])
            if item['status'] == 'Livré':
                status_item.setForeground(Qt.darkGreen)
            else:
                status_item.setForeground(Qt.darkYellow)
            self.frames_table.setItem(row, 6, status_item)

    def save_all(self):
        # 1. Update Patient Info
        db.execute_query(
            "UPDATE patients SET nom=?, prenom=?, phone=?, address=? WHERE id=?",
            (self.nom_input.text(), self.prenom_input.text(), self.phone_input.text(), 
             self.address_input.text(), self.patient_id)
        )

        # 2. Save Prescription
        vl_data = self.vl_grid.get_data()
        vp_data = self.vp_grid.get_data()
        exam_date = self.exam_date.date().toString("yyyy-MM-dd")
        PrescriptionModel.save_prescription(self.patient_id, vl_data, vp_data, exam_date)
        
        # 3. Save Contact Lenses if checked
        if self.contact_lens_grid.isChecked():
            cl_data = self.contact_lens_grid.get_data()
            ContactLensModel.save_lenses(self.patient_id, cl_data, exam_date)
        else:
            db.execute_query("DELETE FROM contact_lenses WHERE patient_id = ?", (self.patient_id,))
        
        QMessageBox.information(self, "Succès", "Informations enregistrées avec succès.")
        self.accept()