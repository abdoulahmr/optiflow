# views/components/contact_lens_grid.py
from PySide6.QtWidgets import (QGroupBox, QGridLayout, QLabel, QDoubleSpinBox, 
                               QLineEdit, QTextEdit, QVBoxLayout, QComboBox)
from PySide6.QtCore import Qt

class ContactLensGrid(QGroupBox):
    def __init__(self, title="Lentilles de Contact"):
        super().__init__(title)
        self.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #E5E7EB; border-radius: 8px; margin-top: 10px; padding-top: 15px; }")
        self.setCheckable(True) # Toggle switch to activate fitting
        self.setChecked(False)
        
        main_layout = QVBoxLayout(self)
        
        # Metadata Fields
        meta_layout = QGridLayout()
        meta_layout.addWidget(QLabel("Type:"), 0, 0)
        self.type_input = QComboBox()
        self.type_input.addItems(["Lentille Souple", "Lentille Rigide", "Lentille Torique"])
        meta_layout.addWidget(self.type_input, 0, 1)
        
        meta_layout.addWidget(QLabel("Marque:"), 0, 2)
        self.marque_input = QLineEdit()
        meta_layout.addWidget(self.marque_input, 0, 3)
        
        meta_layout.addWidget(QLabel("Couleur:"), 1, 0)
        self.color_input = QLineEdit()
        meta_layout.addWidget(self.color_input, 1, 1)
        
        main_layout.addLayout(meta_layout)
        
        # Refraction Grid
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        
        grid_layout.addWidget(QLabel(""), 0, 0)
        od_label = QLabel("OD (Œil Droit)")
        og_label = QLabel("OG (Œil Gauche)")
        od_label.setAlignment(Qt.AlignCenter)
        og_label.setAlignment(Qt.AlignCenter)
        grid_layout.addWidget(od_label, 0, 1)
        grid_layout.addWidget(og_label, 0, 2)

        def make_double_spin():
            sp = QDoubleSpinBox()
            sp.setRange(-30.00, 30.00)
            sp.setSingleStep(0.25)
            sp.setDecimals(2)
            return sp

        # SPH
        grid_layout.addWidget(QLabel("SPH:"), 1, 0)
        self.sph_od = make_double_spin()
        self.sph_og = make_double_spin()
        grid_layout.addWidget(self.sph_od, 1, 1)
        grid_layout.addWidget(self.sph_og, 1, 2)

        # CYL
        grid_layout.addWidget(QLabel("CYL:"), 2, 0)
        self.cyl_od = make_double_spin()
        self.cyl_og = make_double_spin()
        grid_layout.addWidget(self.cyl_od, 2, 1)
        grid_layout.addWidget(self.cyl_og, 2, 2)

        # AXE
        grid_layout.addWidget(QLabel("AXE:"), 3, 0)
        self.axe_od = QDoubleSpinBox()
        self.axe_od.setRange(0, 180)
        self.axe_od.setSuffix("°")
        self.axe_og = QDoubleSpinBox()
        self.axe_og.setRange(0, 180)
        self.axe_og.setSuffix("°")
        grid_layout.addWidget(self.axe_od, 3, 1)
        grid_layout.addWidget(self.axe_og, 3, 2)

        # Diamètre
        grid_layout.addWidget(QLabel("Diamètre:"), 4, 0)
        self.diam_od = QDoubleSpinBox()
        self.diam_od.setRange(0, 30)
        self.diam_od.setSingleStep(0.1)
        self.diam_od.setValue(14.0)
        self.diam_og = QDoubleSpinBox()
        self.diam_og.setRange(0, 30)
        self.diam_og.setSingleStep(0.1)
        self.diam_og.setValue(14.0)
        grid_layout.addWidget(self.diam_od, 4, 1)
        grid_layout.addWidget(self.diam_og, 4, 2)

        # Rayon BC
        grid_layout.addWidget(QLabel("Rayon BC:"), 5, 0)
        self.bc_od = QDoubleSpinBox()
        self.bc_od.setRange(0, 20)
        self.bc_od.setSingleStep(0.1)
        self.bc_od.setValue(8.6)
        self.bc_og = QDoubleSpinBox()
        self.bc_og.setRange(0, 20)
        self.bc_og.setSingleStep(0.1)
        self.bc_og.setValue(8.6)
        grid_layout.addWidget(self.bc_od, 5, 1)
        grid_layout.addWidget(self.bc_og, 5, 2)
        
        main_layout.addLayout(grid_layout)

                # Metadata Fields
        meta_layout = QGridLayout()
        meta_layout.addWidget(QLabel("Type:"), 0, 0)
        self.type_input = QComboBox()
        self.type_input.addItems([
            "Sphérique (Annuelle)",
            "Sphérique (Jetable)",
            "Torique (Annuelle)",
            "Torique (Jetable)",
            "Rigide",
            "Lentille Thérapeutique",
            "Lentille Couleur Esthétique"
        ])
        meta_layout.addWidget(self.type_input, 0, 1)
        
        meta_layout.addWidget(QLabel("Marque:"), 0, 2)
        self.marque_input = QLineEdit()
        meta_layout.addWidget(self.marque_input, 0, 3)
        
        meta_layout.addWidget(QLabel("Couleur:"), 1, 0)
        self.color_input = QLineEdit()
        meta_layout.addWidget(self.color_input, 1, 1)

        # Observations
        main_layout.addWidget(QLabel("Note / Observations:"))
        self.obs_input = QTextEdit()
        self.obs_input.setFixedHeight(50)
        main_layout.addWidget(self.obs_input)

        # Disable inputs if checkbox is unchecked
        self.toggled.connect(self.toggle_inputs)
        self.toggle_inputs(self.isChecked())

    def toggle_inputs(self, checked):
        # PySide6 doesn't support tuples in findChildren, so we loop through types
        widget_types = (QDoubleSpinBox, QLineEdit, QTextEdit, QComboBox)
        for w_type in widget_types:
            for widget in self.findChildren(w_type):
                widget.setEnabled(checked)

    def get_data(self):
        return {
            'type': self.type_input.currentText(),
            'marque': self.marque_input.text(),
            'color': self.color_input.text(),
            'observations': self.obs_input.toPlainText(),
            'od_sph': self.sph_od.value(), 'od_cyl': self.cyl_od.value(), 'od_axe': self.axe_od.value(),
            'od_diametre': self.diam_od.value(), 'od_rayon_bc': self.bc_od.value(),
            'og_sph': self.sph_og.value(), 'og_cyl': self.cyl_og.value(), 'og_axe': self.axe_og.value(),
            'og_diametre': self.diam_og.value(), 'og_rayon_bc': self.bc_og.value()
        }

    def set_data(self, data):
        if not data: return
        self.setChecked(True)
        self.type_input.setCurrentText(data['type'] or "Lentille Souple")
        self.marque_input.setText(data['marque'] or "")
        self.color_input.setText(data['color'] or "")
        self.obs_input.setPlainText(data['observations'] or "")
        
        self.sph_od.setValue(data['od_sph'] or 0.0)
        self.cyl_od.setValue(data['od_cyl'] or 0.0)
        self.axe_od.setValue(data['od_axe'] or 0)
        self.diam_od.setValue(data['od_diametre'] or 14.0)
        self.bc_od.setValue(data['od_rayon_bc'] or 8.6)
        
        self.sph_og.setValue(data['og_sph'] or 0.0)
        self.cyl_og.setValue(data['og_cyl'] or 0.0)
        self.axe_og.setValue(data['og_axe'] or 0)
        self.diam_og.setValue(data['og_diametre'] or 14.0)
        self.bc_og.setValue(data['og_rayon_bc'] or 8.6)