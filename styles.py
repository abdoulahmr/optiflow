from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QPushButton, QHBoxLayout
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QIcon, QImage, QPixmap
from config import resource_path

# ============================================================
# COLORS
# ============================================================
BG = "#F5F7FA"
SIDEBAR = "#111827"
CARD = "#FFFFFF"
TEXT = "#111827"
MUTED = "#6B7280"
PRIMARY = "#2563EB"
PRIMARY_HOVER = "#1D4ED8"
BORDER = "#E5E7EB"
SUCCESS = "#16A34A"
WARNING = "#D97706"
DANGER = "#DC2626"

# ============================================================
# STYLES
# ============================================================
APP_STYLE = f"""
QMainWindow, QWidget {{
    background: {BG};
    font-family: "Segoe UI";
    color: {TEXT};
}}

/* Make labels transparent so they don't show light boxes inside dark frames */
QLabel {{
    background: transparent;
}}

QFrame#sidebar {{
    background: {SIDEBAR};
    border: none;
}}

QLabel#logo {{
    color: white;
    font-size: 24px;
    font-weight: 700;
}}

QLabel#logoSub {{
    color: #9CA3AF;
    font-size: 12px;
}}

QPushButton#navButton {{
    color: #D1D5DB;
    background: transparent;
    border: none;
    border-radius: 8px;
    text-align: left;
    padding: 12px 15px;
    font-size: 14px;
}}

QPushButton#navButton:hover {{
    background: #1F2937;
    color: white;
}}

QPushButton#navButton[selected="true"] {{
    background: {PRIMARY};
    color: white;
}}

QLabel#pageTitle {{
    font-size: 28px;
    font-weight: 700;
}}

QLabel#pageSubtitle {{
    color: {MUTED};
    font-size: 14px;
}}

QFrame#card {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
}}

QLabel#cardTitle {{
    color: {MUTED};
    font-size: 11px;
}}

QLabel#cardValue {{
    color: {TEXT};
    font-size: 20px;
    font-weight: 700;
}}

QLabel#cardChange {{
    font-size: 10px;
    font-weight: 600;
}}

QLineEdit#search {{
    background: white;
    border: 1px solid {BORDER};
    border-radius: 9px;
    padding: 10px 14px;
    font-size: 14px;
}}

QLineEdit#search:focus {{
    border: 1px solid {PRIMARY};
}}

QPushButton#primary {{
    background: {PRIMARY};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 11px 18px;
    font-weight: 600;
}}

QPushButton#primary:hover {{
    background: {PRIMARY_HOVER};
}}

QPushButton#primary:disabled {{
    background: #9CA3AF;
    color: #F3F4F6;
}}

QPushButton#secondary {{
    background: white;
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: 500;
}}

QPushButton#secondary:hover {{
    background: #F9FAFB;
}}

QTableView {{
    background: white;
    border: 1px solid {BORDER};
    border-radius: 10px;
    gridline-color: transparent;
    font-size: 13px;
}}

QTableView::item {{
    padding: 8px;
    border-bottom: 1px solid #F3F4F6;
}}

QHeaderView::section {{
    background: #F9FAFB;
    color: {MUTED};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 11px;
    font-size: 12px;
    font-weight: 600;
}}

QScrollBar:vertical {{
    width: 8px;
    background: transparent;
}}

QScrollBar::handle:vertical {{
    background: #D1D5DB;
    border-radius: 4px;
}}
"""

# ============================================================
# CARD
# ============================================================
class StatCard(QFrame):
    def __init__(self, title, value, change, change_color=SUCCESS):
        super().__init__()
        self.setObjectName("card")
        self.setFixedHeight(75)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(2)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")

        self.value_label = QLabel(value)
        self.value_label.setObjectName("cardValue")

        change_label = QLabel(change)
        change_label.setObjectName("cardChange")
        change_label.setStyleSheet(f"color: {change_color};")

        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(change_label)

# ============================================================
# SIDEBAR
# ============================================================
class Sidebar(QFrame):
    # Signal pour changer de page
    page_changed = Signal(int)

    def __init__(self, user=None):
        super().__init__()
        self.setObjectName("sidebar")
        self.setAttribute(Qt.WA_StyledBackground, True)  # Fixes background transparency
        self.setFixedWidth(230)
        self.setFrameShape(QFrame.NoFrame)
        
        # Force the dark background directly on this widget
        self.setStyleSheet(f"QFrame#sidebar {{ background: {SIDEBAR}; border: none; }}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 25, 15, 20)
        layout.setSpacing(6)

        # Logo
        logo = QLabel("OptiFlow")
        logo.setObjectName("logo")
        subtitle = QLabel("Caisse & ERP")
        subtitle.setObjectName("logoSub")

        layout.addWidget(logo)
        layout.addWidget(subtitle)
        layout.addSpacing(30)

        self.buttons = []
        
        # Explicit IDs for each module so QStackedWidget matches perfectly
        # 0: Dashboard, 1: POS, 2: Patients, 3: Matrix, 4: Catalogue, 
        # 5: Finance, 6: Inventory, 7: Suppliers, 8: Settings
        all_menu_items = [
            {"id": 0, "icon": "assets/icons/dashboard.png", "text": "Tableau de bord"},
            {"id": 1, "icon": "assets/icons/add.png", "text": "Nouvelle Prescription"},
            {"id": 2, "icon": "assets/icons/customer.png", "text": "Fiche Client"},
            {"id": 3, "icon": "assets/icons/eye.png", "text": "Matrice des Verres"},
            {"id": 4, "icon": "assets/icons/catalogue.png", "text": "Catalogue"},
            {"id": 5, "icon": "assets/icons/budget.png", "text": "Finance"},
            {"id": 6, "icon": "assets/icons/in-stock.png", "text": "Gestion du Stock"},
            {"id": 7, "icon": "assets/icons/supplier.png", "text": "Fournisseurs"},
            {"id": 8, "icon": "assets/icons/setting.png", "text": "Paramètres"},
        ]
        
        # Define allowed IDs based on role
        allowed_ids = [0, 1, 2, 3, 4] # Default for non-admins
        if user and user['role'] == 'Administrateur':
            allowed_ids = [item['id'] for item in all_menu_items] # Admin gets all
            
        # Filter the menu
        menu = [item for item in all_menu_items if item['id'] in allowed_ids]

        for item in menu:
            button = QPushButton(item['text'])
            button.setObjectName("navButton")
            button.setCursor(Qt.PointingHandCursor)
            
            # Load icon normally
            button.setIcon(QIcon(resource_path(item['icon'])))
            button.setIconSize(QSize(20, 20))

            if item['id'] == 0:
                button.setProperty("selected", True)

            # Pass the explicit ID to the signal
            button.clicked.connect(lambda checked=False, pid=item['id'], b=button: self.select_button(pid, b))
            layout.addWidget(button)
            self.buttons.append(button)

        layout.addStretch()

        # User profile section
        user_frame = QFrame()
        user_layout = QHBoxLayout(user_frame) # Restored to QHBoxLayout for a cleaner look
        user_layout.setContentsMargins(10, 10, 10, 10)
        user_layout.setSpacing(10)
        
        status_dot = QLabel("●")
        status_dot.setStyleSheet("color: #16A34A; font-size: 14px;")
        
        if user:
            username = user['username']
            role = user['role']
        else:
            username = "Invité"
            role = "Non connecté"
            
        user_info = QLabel(f"{username}\n{role}")
        user_info.setStyleSheet("color: #D1D5DB; font-size: 12px;")
        
        user_layout.addWidget(status_dot)
        user_layout.addWidget(user_info)
        user_layout.addStretch()
        
        layout.addWidget(user_frame)

    def select_button(self, page_id, selected):
        for button in self.buttons:
            button.setProperty("selected", button == selected)
            button.style().unpolish(button)
            button.style().polish(button)
            
        self.page_changed.emit(page_id)