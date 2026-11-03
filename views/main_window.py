# views/main_window.py
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, 
                               QStackedWidget, QVBoxLayout, QLabel, 
                               QScrollArea, QApplication)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from styles import Sidebar, StatCard, BG

from views.dashboard_tab.dashboard_view import DashboardView
from views.pos_tab.pos_view import POSView
from views.patients_tab.patients_view import PatientsView
from views.lenses_tab.matrix_view import MatrixView
from views.catalogue_tab.catalogue_view import CatalogueView
from views.finance_tab.finance_view import FinanceView
from views.inventory_tab.inventory_view import InventoryView
from views.suppliers_tab.suppliers_view import SuppliersView
from views.settings_tab.settings_view import SettingsView

class PlaceholderPage(QWidget):
    """A temporary page class to show UI structure before we build each module."""
    def __init__(self, title, subtitle):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(10)
        title_label = QLabel(title)
        title_label.setObjectName("pageTitle")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("pageSubtitle")
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addStretch()

class MainWindow(QMainWindow):
    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user
        
        self.setWindowTitle("OptiFlow - Caisse & ERP")
        self.resize(1200, 750)
        self.setWindowIcon(QIcon("assets/icons/icon.png"))
        
        central_widget = QWidget()
        central_widget.setStyleSheet("background: transparent;")
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = Sidebar(self.current_user)
        main_layout.addWidget(self.sidebar)

        self.stacked_widget = QStackedWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        content_container = QWidget()
        content_container.setStyleSheet(f"background: {BG};")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.stacked_widget)
        scroll_area.setWidget(content_container)
        
        main_layout.addWidget(scroll_area, 1)

        self.setup_pages()
        self.sidebar.page_changed.connect(self.on_page_changed)

    def on_page_changed(self, index):
        self.stacked_widget.setCurrentIndex(index)
        app = QApplication.instance()
        
        # Index 2: Fiche Client
        if index == 2:
            if hasattr(self.stacked_widget.widget(2), 'load_patients'):
                self.stacked_widget.widget(2).load_patients()
        
        # Index 3: Matrice des Verres — ONLY reload if dirty!
        elif index == 3:
            if getattr(app, 'matrix_dirty', False):
                self.matrix_view.reload_data()
                app.matrix_dirty = False
            # If not dirty, do nothing — the matrix is already built!
        
        # Index 4: Catalogue
        elif index == 4:
            if getattr(app, 'catalogue_dirty', True):
                self.catalogue_view.load_data()
                app.catalogue_dirty = False
        
        # Index 5: Finance
        elif index == 5:
            if getattr(app, 'finance_dirty', True):
                self.finance_view.load_data()
                app.finance_dirty = False
                
    def setup_pages(self):
        # Index 0: Tableau de bord
        self.stacked_widget.addWidget(DashboardView())
        # Index 1: Nouvelle Prescription
        self.stacked_widget.addWidget(POSView())
        # Index 2: Fiche Client
        self.stacked_widget.addWidget(PatientsView())
        # Index 3: Matrice des Verres
        self.matrix_view = MatrixView(self.current_user)
        self.stacked_widget.addWidget(self.matrix_view)
        # Index 4: Catalogue
        self.catalogue_view = CatalogueView()
        self.stacked_widget.addWidget(self.catalogue_view)
        # Index 5: Finance
        self.finance_view = FinanceView()
        self.stacked_widget.addWidget(self.finance_view)
        # Index 6: Gestion du Stock
        self.stacked_widget.addWidget(InventoryView())
        # Index 7: Fournisseurs
        self.stacked_widget.addWidget(SuppliersView())
        # Index 8: Paramètres
        self.stacked_widget.addWidget(SettingsView())