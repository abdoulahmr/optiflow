# views/components/refraction_grid.py
from PySide6.QtWidgets import (QGroupBox, QGridLayout, QLabel, QDoubleSpinBox, QSpinBox)
from PySide6.QtCore import Qt

class RefractionGrid(QGroupBox):
    def __init__(self, title="Correction Optique"):
        super().__init__(title)
        self.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #E5E7EB; border-radius: 8px; margin-top: 10px; padding-top: 15px; }")
        
        layout = QGridLayout(self)
        layout.setSpacing(10)
        
        # Headers
        layout.addWidget(QLabel(""), 0, 0)
        od_label = QLabel("OD (Œil Droit)")
        og_label = QLabel("OG (Œil Gauche)")
        od_label.setAlignment(Qt.AlignCenter)
        og_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(od_label, 0, 1)
        layout.addWidget(og_label, 0, 2)

        # Helper to create decimal spinboxes (for SPH, CYL, ADD)
        def make_double_spin():
            sp = QDoubleSpinBox()
            sp.setRange(-30.00, 30.00)
            sp.setSingleStep(0.25)
            sp.setDecimals(2)
            return sp

        # Helper to create integer spinboxes (for AXE)
        def make_int_spin():
            sp = QSpinBox()
            sp.setRange(0, 180)
            sp.setSuffix("°")
            return sp

        # 1. SPH
        layout.addWidget(QLabel("SPH:"), 1, 0)
        self.sph_od = make_double_spin()
        self.sph_og = make_double_spin()
        layout.addWidget(self.sph_od, 1, 1)
        layout.addWidget(self.sph_og, 1, 2)

        # 2. CYL
        layout.addWidget(QLabel("CYL:"), 2, 0)
        self.cyl_od = make_double_spin()
        self.cyl_og = make_double_spin()
        layout.addWidget(self.cyl_od, 2, 1)
        layout.addWidget(self.cyl_og, 2, 2)

        # 3. AXE
        layout.addWidget(QLabel("AXE:"), 3, 0)
        self.axe_od = make_int_spin()
        self.axe_og = make_int_spin()
        layout.addWidget(self.axe_od, 3, 1)
        layout.addWidget(self.axe_og, 3, 2)

        # 4. ADD
        layout.addWidget(QLabel("ADD:"), 4, 0)
        self.add_od = make_double_spin()
        self.add_og = make_double_spin()
        layout.addWidget(self.add_od, 4, 1)
        layout.addWidget(self.add_og, 4, 2)

    def get_data(self):
        return {
            'sph_od': self.sph_od.value(),
            'cyl_od': self.cyl_od.value(),
            'axe_od': self.axe_od.value(),
            'add_od': self.add_od.value(),
            'sph_og': self.sph_og.value(),
            'cyl_og': self.cyl_og.value(),
            'axe_og': self.axe_og.value(),
            'add_og': self.add_og.value(),
        }

    def set_data(self, data):
        if not data: return
        self.sph_od.setValue(data['vl_sph_od'] or 0.0)
        self.cyl_od.setValue(data['vl_cyl_od'] or 0.0)
        self.axe_od.setValue(data['vl_axe_od'] or 0)
        self.add_od.setValue(data['vl_add_od'] or 0.0)
        
        self.sph_og.setValue(data['vl_sph_og'] or 0.0)
        self.cyl_og.setValue(data['vl_cyl_og'] or 0.0)
        self.axe_og.setValue(data['vl_axe_og'] or 0)
        self.add_og.setValue(data['vl_add_og'] or 0.0)

#