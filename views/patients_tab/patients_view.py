# views/patients_tab/patients_view.py
from PySide6.QtWidgets import (QHeaderView, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QTableView)
from PySide6.QtCore import Qt, QAbstractTableModel
from models.patient_model import PatientModel
from views.patients_tab.patient_dialog import PatientDialog
from views.patients_tab.patient_profile_dialog import PatientProfileDialog

class PatientTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self.headers = ["ID", "Nom", "Prénom", "Âge", "Téléphone", "Dernière Correction (Date | OD | OG)"]

    def data(self, index, role):
        if role == Qt.DisplayRole:
            row = self._data[index.row()]
            keys = ["id", "nom", "prenom", "age", "phone", "last_rx"]
            
            if index.column() == 5: # The new Correction column
                if row['last_exam']:
                    od_sph = f"{row['vl_sph_od']:.2f}" if row['vl_sph_od'] is not None else "0.00"
                    od_cyl = f"{row['vl_cyl_od']:.2f}" if row['vl_cyl_od'] is not None else "0.00"
                    og_sph = f"{row['vl_sph_og']:.2f}" if row['vl_sph_og'] is not None else "0.00"
                    og_cyl = f"{row['vl_cyl_og']:.2f}" if row['vl_cyl_og'] is not None else "0.00"
                    
                    return f"{row['last_exam']} | OD: {od_sph} ({od_cyl}) | OG: {og_sph} ({og_cyl})"
                else:
                    return "Aucune ordonnance"
            
            value = row[keys[index.column()]]
            return str(value) if value is not None else ""
        return None

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self.headers)

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None
    
class PatientsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # 1. Header
        title = QLabel("Fiche Client")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Gérez les dossiers de vos patients")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        # 2. Action Bar (Search & Add Button)
        action_bar = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search")
        self.search_input.setPlaceholderText("Rechercher par nom, prénom ou téléphone...")
        self.search_input.textChanged.connect(self.load_patients)
        
        self.add_btn = QPushButton("＋ Ajouter Client")
        self.add_btn.setObjectName("primary")
        self.add_btn.setStyleSheet("""
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
        self.add_btn.clicked.connect(self.open_add_patient_dialog)
        
        action_bar.addWidget(self.search_input)
        action_bar.addWidget(self.add_btn)
        layout.addLayout(action_bar)

        # 3. Table
        self.table = QTableView()
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setEditTriggers(QTableView.NoEditTriggers)
        self.table.horizontalHeader().stretchLastSection = True
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents) # <--- ADD THIS LINE
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self.open_patient_profile)
        layout.addWidget(self.table)

        # Load initial data
        self.load_patients()

    def load_patients(self):
        search_term = self.search_input.text()
        patients = PatientModel.get_all_patients(search_term)
        self.model = PatientTableModel(patients)
        self.table.setModel(self.model)

    def open_add_patient_dialog(self):
        dialog = PatientDialog(self)
        if dialog.exec():
            self.load_patients() # Refresh table after adding

    def open_patient_profile(self, index):
        # Get the ID from the first column of the clicked row
        row = index.row()
        patient_id = self.model._data[row]["id"]
        
        dialog = PatientProfileDialog(patient_id, self)
        dialog.exec()