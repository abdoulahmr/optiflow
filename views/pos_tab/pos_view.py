# views/pos_tab/pos_view.py
from PySide6.QtWidgets import (QSizePolicy, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel,
                               QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QMessageBox, QLineEdit, QCompleter,
                               QApplication, QFrame, QStackedWidget, QButtonGroup,
                               QListWidget, QListWidgetItem, QStyledItemDelegate,
                               QStyle, QAbstractItemView)
from PySide6.QtCore import Qt, QStringListModel, Signal, QSize, QRect
from PySide6.QtGui import QPainter, QColor, QFont, QFontMetrics

from models.patient_model import PatientModel
from models.inventory_model import InventoryModel
from models.lens_model import LensModel
from database.db_manager import db
from styles import (PRIMARY, PRIMARY_HOVER, CARD, TEXT, MUTED, BORDER,
                    SUCCESS, WARNING, DANGER)
from views.pos_tab.settlement_dialog import SettlementDialog
from views.pos_tab.pending_orders_dialog import PendingOrdersDialog

from models.patient_model import PatientModel
from views.components.receipt_view import ReceiptViewDialog
from models.inventory_model import CONTACT_LENS_TYPES

# ============================================================
# HELPERS
# ============================================================
SOFT_PRIMARY = "#EFF6FF"


def fmt_num(value):
    """1234.5 -> '1 234.50'"""
    return f"{value:,.2f}".replace(",", " ")


def fmt_da(value):
    return f"{fmt_num(value)} DA"


def fmt_sign(v):
    return f"+{v:.2f}" if v >= 0 else f"{v:.2f}"


def parse_patient_id(text):
    """Extracts the patient id from 'Nom Prénom (ID: 12)'. Returns None if absent."""
    if "ID:" not in text:
        return None
    try:
        return int(text.split("ID:")[1].replace(")", "").strip())
    except Exception:
        return None


# Badge colours per cart line type: (background, text)
TYPE_BADGES = {
    "Verre": ("#EFF6FF", "#1D4ED8"),
    "Lentilles": ("#ECFDF5", "#047857"),
    "Monture": ("#FFF7ED", "#C2410C"),
    "Montures": ("#FFF7ED", "#C2410C"),
    "Lunettes de Soleil": ("#FEF9C3", "#A16207"),  
    "Accessoires": ("#F3E8FF", "#7C3AED"),        
    "Service": ("#FCE7F3", "#BE185D"),              
}
DEFAULT_BADGE = ("#F3F4F6", "#4B5563")


POS_QSS = f"""
QLabel#pageTitle {{
    font-size: 24px;
    font-weight: 700;
}}

QWidget#plain {{
    background: transparent;
}}

QFrame#panel {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
}}

QLabel#panelTitle {{
    font-size: 14px;
    font-weight: 700;
    color: {TEXT};
}}

QLabel#fieldLabel {{
    font-size: 12px;
    font-weight: 600;
    color: {MUTED};
}}

QLabel#countPill {{
    background: {SOFT_PRIMARY};
    color: {PRIMARY};
    border-radius: 10px;
    padding: 2px 9px;
    font-size: 12px;
    font-weight: 700;
}}

QLabel#emptyTitle {{
    font-size: 15px;
    font-weight: 600;
    color: {TEXT};
}}

QLabel#emptyHint {{
    font-size: 13px;
    color: {MUTED};
}}

QLineEdit#field, QComboBox#field {{
    background: white;
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    min-height: 20px;
}}

QLineEdit#field:focus, QComboBox#field:focus {{
    border: 1px solid {PRIMARY};
}}

QComboBox#field:disabled {{
    background: #F3F4F6;
    color: #9CA3AF;
}}

QFrame#segmented {{
    background: #F3F4F6;
    border: none;
    border-radius: 10px;
}}

QPushButton#segBtn {{
    background: transparent;
    border: none;
    border-radius: 8px;
    padding: 8px 10px;
    color: {MUTED};
    font-size: 13px;
    font-weight: 600;
}}

QPushButton#segBtn:hover {{
    color: {TEXT};
}}

QPushButton#segBtn:checked {{
    background: white;
    color: {PRIMARY};
}}

QListWidget#itemList {{
    background: white;
    border: 1px solid {BORDER};
    border-radius: 10px;
    outline: none;
    padding: 4px;
}}

QTableWidget#cartTable {{
    background: white;
    border: none;
    border-radius: 0px;
    outline: none;
}}

QTableWidget#cartTable::item {{
    padding: 4px 8px;
    border-bottom: 1px solid #F3F4F6;
}}

QPushButton#removeBtn {{
    background: transparent;
    color: #9CA3AF;
    border: none;
    border-radius: 6px;
    font-size: 14px;
}}

QPushButton#removeBtn:hover {{
    background: #FEF2F2;
    color: {DANGER};
}}

QPushButton#linkBtn {{
    background: transparent;
    color: {MUTED};
    border: none;
    padding: 4px 8px;
    font-size: 12px;
    font-weight: 600;
}}

QPushButton#linkBtn:hover {{
    color: {DANGER};
}}

QPushButton#debtBtn {{
    background: #FEF2F2;
    color: {DANGER};
    border: 1px solid #FECACA;
    border-radius: 8px;
    padding: 9px 16px;
    font-size: 13px;
    font-weight: 600;
}}

QPushButton#debtBtn:hover {{
    background: #FEE2E2;
    border: 1px solid {DANGER};
}}

QFrame#preview {{
    background: #F9FAFB;
    border: 1px solid {BORDER};
    border-radius: 10px;
}}

QFrame#divider {{
    background: {BORDER};
    border: none;
    max-height: 1px;
    min-height: 1px;
}}

QLabel#sumLabel {{
    font-size: 13px;
    color: {MUTED};
}}

QLabel#sumValue {{
    font-size: 13px;
    font-weight: 600;
    color: {TEXT};
}}

QLabel#totalLabel {{
    font-size: 14px;
    font-weight: 600;
    color: {TEXT};
}}

QLabel#totalValue {{
    font-size: 28px;
    font-weight: 700;
    color: {PRIMARY};
}}

QPushButton#primary {{
    background: {PRIMARY};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 14px;
    font-weight: 600;
}}

QPushButton#primary:hover {{
    background: {PRIMARY_HOVER};
}}

QPushButton#primary:disabled {{
    background: #9CA3AF;
    color: #F3F4F6;
}}
"""


def make_plain(widget):
    """Marks a container as transparent so it doesn't paint the app's grey background inside a white panel."""
    widget.setObjectName("plain")
    return widget


# ============================================================
# SEGMENTED CONTROL
# ============================================================
class Segmented(QFrame):
    """A compact pill-style selector. options = [(label, value), ...]"""
    changed = Signal(int)

    def __init__(self, options):
        super().__init__()
        self.setObjectName("segmented")
        self._values = [value for _, value in options]
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(2)

        for i, (label, _) in enumerate(options):
            btn = QPushButton(label)
            btn.setObjectName("segBtn")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setChecked(i == 0)
            self._group.addButton(btn, i)
            layout.addWidget(btn, 1)

        self._group.idClicked.connect(self.changed)

    def currentIndex(self):
        return self._group.checkedId()

    def currentText(self):
        return self._values[self.currentIndex()]

    def setCurrentIndex(self, index):
        button = self._group.button(index)
        if button:
            button.setChecked(True)


# ============================================================
# SEARCHABLE ITEM LIST (frames, accessories, contact lenses)
# ============================================================
class ItemDelegate(QStyledItemDelegate):
    ROW_HEIGHT = 56

    def __init__(self, picker):
        super().__init__(picker.list)
        self.picker = picker

    def sizeHint(self, option, index):
        return QSize(option.rect.width(), self.ROW_HEIGHT)

    def paint(self, painter, option, index):
        item = index.data(Qt.UserRole)
        if item is None:
            return

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        rect = option.rect.adjusted(2, 2, -2, -2)
        selected = bool(option.state & QStyle.State_Selected)
        hovered = bool(option.state & QStyle.State_MouseOver)

        if selected:
            painter.setPen(QColor(PRIMARY))
            painter.setBrush(QColor(SOFT_PRIMARY))
            painter.drawRoundedRect(rect, 8, 8)
        elif hovered:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#F9FAFB"))
            painter.drawRoundedRect(rect, 8, 8)

        available = self.picker.available(item)
        inner = rect.adjusted(12, 9, -12, -9)

        # Price (right)
        price_font = QFont(option.font)
        price_font.setPixelSize(13)
        price_font.setBold(True)
        price_text = fmt_da(item['retail_price'])
        price_width = QFontMetrics(price_font).horizontalAdvance(price_text)
        painter.setFont(price_font)
        painter.setPen(QColor(TEXT if available > 0 else MUTED))
        painter.drawText(QRect(inner.right() - price_width, inner.top(), price_width, 18),
                         Qt.AlignRight | Qt.AlignVCenter, price_text)

        # Name (left, elided)
        name_font = QFont(option.font)
        name_font.setPixelSize(13)
        name_font.setWeight(QFont.Weight.DemiBold)
        name_width = inner.width() - price_width - 12
        name = QFontMetrics(name_font).elidedText(str(item['name']), Qt.ElideRight, name_width)
        painter.setFont(name_font)
        painter.setPen(QColor(TEXT if available > 0 else MUTED))
        painter.drawText(QRect(inner.left(), inner.top(), name_width, 18),
                         Qt.AlignLeft | Qt.AlignVCenter, name)

        # Sub line: category + stock
        sub_font = QFont(option.font)
        sub_font.setPixelSize(11)
        painter.setFont(sub_font)
        if available <= 0:
            sub_text, sub_color = f"{item['category']}   Rupture de stock", DANGER
        elif available <= 3:
            sub_text, sub_color = f"{item['category']}   Stock faible : {available}", WARNING
        else:
            sub_text, sub_color = f"{item['category']}   Stock : {available}", MUTED
        painter.setPen(QColor(sub_color))
        painter.drawText(QRect(inner.left(), inner.top() + 22, inner.width(), 16),
                         Qt.AlignLeft | Qt.AlignVCenter, sub_text)

        painter.restore()


class ItemPicker(QWidget):
    """Search box + list of inventory items + add button."""
    add_requested = Signal(object)

    def __init__(self, placeholder):
        super().__init__()
        make_plain(self)
        self._items = []
        self.in_cart = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.search = QLineEdit()
        self.search.setObjectName("field")
        self.search.setPlaceholderText(placeholder)
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._apply_filter)
        layout.addWidget(self.search)

        self.list = QListWidget()
        self.list.setObjectName("itemList")
        self.list.setMouseTracking(True)
        self.list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list.setFixedHeight(232)
        self.list.setItemDelegate(ItemDelegate(self))
        self.list.itemSelectionChanged.connect(self._update_button)
        self.list.itemDoubleClicked.connect(lambda _: self._emit_add())
        layout.addWidget(self.list, 1)

        self.empty_label = QLabel("Aucun article trouvé")
        self.empty_label.setObjectName("emptyHint")
        self.empty_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.empty_label)

        self.add_btn = QPushButton("Ajouter au panier")
        self.add_btn.setObjectName("primary")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setEnabled(False)
        self.add_btn.clicked.connect(self._emit_add)
        layout.addWidget(self.add_btn)

    # ---- data ----
    def set_items(self, items):
        self._items = list(items)
        self._apply_filter()

    def available(self, item):
        return item['stock_qty'] - self.in_cart.get(item['id'], 0)

    def set_cart_counts(self, counts):
        self.in_cart = counts
        self.list.viewport().update()

    def selected_item(self):
        current = self.list.currentItem()
        return current.data(Qt.UserRole) if current else None

    # ---- internals ----
    def _apply_filter(self):
        needle = self.search.text().strip().lower()
        self.list.clear()
        for item in self._items:
            haystack = f"{item['name']} {item['category']}".lower()
            if needle in haystack:
                row = QListWidgetItem()
                row.setData(Qt.UserRole, item)
                row.setSizeHint(QSize(0, ItemDelegate.ROW_HEIGHT))
                self.list.addItem(row)
        self.empty_label.setVisible(self.list.count() == 0)
        self._update_button()

    def _update_button(self):
        self.add_btn.setEnabled(self.selected_item() is not None)

    def _emit_add(self):
        item = self.selected_item()
        if item is not None:
            self.add_requested.emit(item)


# ============================================================
# POS VIEW
# ============================================================
class POSView(QWidget):
    def __init__(self):
        super().__init__()
        self.cart_items = []
        self.selected_patient_id = None
        self.patient_map = {}
        self.setStyleSheet(POS_QSS)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(18)

        root.addLayout(self._build_header())

        body = QHBoxLayout()
        body.setSpacing(18)
        body.addLayout(self._build_left_column(), 3)
        body.addWidget(self._build_right_column(), 2, Qt.AlignTop)
        root.addLayout(body, 1)

        # Signals (after every widget exists)
        self.lens_type.changed.connect(self.update_lens_groups)
        self.lens_group.currentTextChanged.connect(self.update_lens_sph_cyl_options)
        self.lens_treatment.currentIndexChanged.connect(self.refresh_lens_preview)
        self.lens_sph.currentIndexChanged.connect(self.refresh_lens_preview)
        self.lens_cyl.currentIndexChanged.connect(self.refresh_lens_preview)
        self.lens_vision.changed.connect(self.refresh_lens_preview)

        # Initial data
        self.load_inventory_items()
        self.load_contact_lenses()
        self.load_treatments()
        self.update_lens_groups()
        self.refresh_cart()
        self._update_patient_status()

    # --------------------------------------------------------
    # UI BUILDERS
    # --------------------------------------------------------
    def _panel(self):
        panel = QFrame()
        panel.setObjectName("panel")
        return panel

    def _build_header(self):
        header = QHBoxLayout()
        header.setSpacing(12)

        titles = QVBoxLayout()
        titles.setSpacing(2)
        title = QLabel("Nouvelle Prescription")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Créer une ordonnance et finaliser la vente")
        subtitle.setObjectName("pageSubtitle")
        titles.addWidget(title)
        titles.addWidget(subtitle)
        header.addLayout(titles)
        header.addStretch()

        debt_btn = QPushButton("Règlement Dettes")
        debt_btn.setObjectName("debtBtn")
        debt_btn.setCursor(Qt.PointingHandCursor)
        debt_btn.clicked.connect(self.open_pending_orders)
        header.addWidget(debt_btn, 0, Qt.AlignVCenter)
        return header

    # ---------------- LEFT: patient, cart, summary ----------------
    def _build_left_column(self):
        column = QVBoxLayout()
        column.setSpacing(14)
        column.addWidget(self._build_patient_panel())
        column.addWidget(self._build_cart_panel())
        column.addWidget(self._build_summary_panel())
        column.addStretch()
        return column

    def _build_patient_panel(self):
        panel = self._panel()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 14, 18, 16)
        layout.setSpacing(10)

        head = QHBoxLayout()
        head_title = QLabel("Patient")
        head_title.setObjectName("panelTitle")
        self.patient_status = QLabel()
        head.addWidget(head_title)
        head.addStretch()
        head.addWidget(self.patient_status)
        layout.addLayout(head)

        self.patient_search = QLineEdit()
        self.patient_search.setObjectName("field")
        self.patient_search.setPlaceholderText("Tapez le nom du client...")
        self.patient_search.setClearButtonEnabled(True)

        self.patient_completer = QCompleter()
        self.patient_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.patient_completer.setFilterMode(Qt.MatchContains)
        self.patient_search.setCompleter(self.patient_completer)

        self.patient_search.textChanged.connect(self._on_patient_text_changed)
        self.patient_completer.activated.connect(self.on_patient_selected)
        layout.addWidget(self.patient_search)
        return panel

    def _build_cart_panel(self):
        panel = self._panel()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        head_wrap = make_plain(QWidget())
        head = QHBoxLayout(head_wrap)
        head.setContentsMargins(18, 14, 14, 12)
        head.setSpacing(8)
        title = QLabel("Panier")
        title.setObjectName("panelTitle")
        self.count_pill = QLabel("0")
        self.count_pill.setObjectName("countPill")
        self.clear_btn = QPushButton("Vider le panier")
        self.clear_btn.setObjectName("linkBtn")
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.clicked.connect(self.clear_cart)
        head.addWidget(title)
        head.addWidget(self.count_pill)
        head.addStretch()
        head.addWidget(self.clear_btn)
        layout.addWidget(head_wrap)

        divider = QFrame()
        divider.setObjectName("divider")
        layout.addWidget(divider)

        # Stack: empty state / table
        self.cart_stack = make_plain(QStackedWidget())

        empty = make_plain(QWidget())
        empty_layout = QVBoxLayout(empty)
        empty_layout.setAlignment(Qt.AlignCenter)
        empty_layout.setSpacing(6)
        empty_title = QLabel("Le panier est vide")
        empty_title.setObjectName("emptyTitle")
        empty_title.setAlignment(Qt.AlignCenter)
        empty_hint = QLabel("Ajoutez des verres, une monture ou des lentilles\ndepuis le panneau de droite.")
        empty_hint.setObjectName("emptyHint")
        empty_hint.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(empty_title)
        empty_layout.addWidget(empty_hint)
        self.cart_stack.addWidget(empty)

        self.cart_table = QTableWidget()
        self.cart_table.setObjectName("cartTable")
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["Type", "Description", "Prix (DA)", "Remise (DA)", ""])
        header = self.cart_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.cart_table.setColumnWidth(0, 110)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.cart_table.setColumnWidth(4, 48)
        header.setHighlightSections(False)
        self.cart_table.verticalHeader().setVisible(False)
        self.cart_table.verticalHeader().setDefaultSectionSize(46)
        self.cart_table.setShowGrid(False)
        self.cart_table.setWordWrap(True)
        self.cart_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.cart_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.cart_table.setFocusPolicy(Qt.NoFocus)
        self.cart_stack.addWidget(self.cart_table)

        self.cart_stack.setFixedHeight(190)
        layout.addWidget(self.cart_stack)
        return panel

    def _build_summary_panel(self):
        panel = self._panel()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(8)

        def line(label_text, value_label):
            row = make_plain(QWidget())
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            label = QLabel(label_text)
            label.setObjectName("sumLabel")
            value_label.setObjectName("sumValue")
            value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row_layout.addWidget(label)
            row_layout.addStretch()
            row_layout.addWidget(value_label)
            return row

        self.subtotal_label = QLabel("0.00 DA")
        self.discount_label = QLabel("0.00 DA")
        layout.addWidget(line("Sous-total", self.subtotal_label))
        self.discount_row = line("Remises", self.discount_label)
        layout.addWidget(self.discount_row)

        divider = QFrame()
        divider.setObjectName("divider")
        layout.addWidget(divider)

        total_row = QHBoxLayout()
        total_title = QLabel("Total à payer")
        total_title.setObjectName("totalLabel")
        self.total_label = QLabel("0.00 DA")
        self.total_label.setObjectName("totalValue")
        self.total_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_row.addWidget(total_title)
        total_row.addStretch()
        total_row.addWidget(self.total_label)
        layout.addLayout(total_row)

        layout.addSpacing(4)
        self.checkout_btn = QPushButton("Finaliser la vente")
        self.checkout_btn.setObjectName("primary")
        self.checkout_btn.setStyleSheet("font-size: 15px;")
        self.checkout_btn.setMinimumHeight(52)
        self.checkout_btn.setCursor(Qt.PointingHandCursor)
        self.checkout_btn.clicked.connect(self.open_settlement)
        layout.addWidget(self.checkout_btn)
        return panel

    # ---------------- RIGHT: add items ----------------
    def _build_right_column(self):
        panel = self._panel()
        panel.setMinimumWidth(400)
        panel.setMaximumWidth(480)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(14)

        title = QLabel("Ajouter au panier")
        title.setObjectName("panelTitle")
        layout.addWidget(title)

        # CHANGED: Added "Soleil" and "Service" tabs
        self.add_tabs = Segmented([
            ("Verres", "lens"),
            ("Montures", "frame"),
            ("Lentilles", "contact"),
            ("Soleil", "sun"),
            ("Service", "service")
        ])
        layout.addWidget(self.add_tabs)

        self.add_stack = make_plain(QStackedWidget())
        self.add_stack.addWidget(self._build_lens_page())

        self.frame_picker = ItemPicker("Rechercher une monture ou un accessoire...")
        self.frame_picker.add_requested.connect(self.add_inventory_item)
        self.add_stack.addWidget(self.frame_picker)

        self.cl_page = self._build_contact_lens_page()
        self.add_stack.addWidget(self.cl_page)

        # NEW: Sunglasses picker
        self.sun_picker = ItemPicker("Rechercher des lunettes de soleil...")
        self.sun_picker.add_requested.connect(self.add_inventory_item)
        self.add_stack.addWidget(self.sun_picker)

        # NEW: Repair / Service page
        self.add_stack.addWidget(self._build_repair_page())

        self.add_tabs.changed.connect(self._on_add_tab_changed)
        self._on_add_tab_changed(0)
        layout.addWidget(self.add_stack)
        return panel

    def _on_add_tab_changed(self, index):
        """Switch page and let the panel shrink to the height of the visible page only."""
        self.add_stack.setCurrentIndex(index)
        for i in range(self.add_stack.count()):
            page = self.add_stack.widget(i)
            policy = QSizePolicy.Preferred if i == index else QSizePolicy.Ignored
            page.setSizePolicy(QSizePolicy.Preferred, policy)
        self.add_stack.updateGeometry()

    def _build_lens_page(self):
        page = make_plain(QWidget())
        grid = QGridLayout(page)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(6)

        def field_label(text):
            label = QLabel(text)
            label.setObjectName("fieldLabel")
            return label

        def combo():
            c = QComboBox()
            c.setObjectName("field")
            return c

        self.lens_type = Segmented([("Transparent", "Transparent"),
                                    ("Photochromique", "Photochromique"),
                                    ("Spéciale", "Speciale")])
        self.lens_group = combo()
        self.lens_treatment = combo()
        self.lens_sph = combo()
        self.lens_cyl = combo()
        self.lens_vision = Segmented([("Vision de loin", "VL (Loin)"),
                                      ("Vision de près", "VP (Près)")])

        grid.addWidget(field_label("Type de verre"), 0, 0, 1, 2)
        grid.addWidget(self.lens_type, 1, 0, 1, 2)

        grid.addWidget(field_label("Groupe optique"), 2, 0)
        grid.addWidget(field_label("Traitement"), 2, 1)
        grid.addWidget(self.lens_group, 3, 0)
        grid.addWidget(self.lens_treatment, 3, 1)

        grid.addWidget(field_label("Sphère (SPH)"), 4, 0)
        grid.addWidget(field_label("Cylindre (CYL)"), 4, 1)
        grid.addWidget(self.lens_sph, 5, 0)
        grid.addWidget(self.lens_cyl, 5, 1)

        grid.addWidget(field_label("Vision"), 6, 0, 1, 2)
        grid.addWidget(self.lens_vision, 7, 0, 1, 2)

        grid.setRowMinimumHeight(8, 8)

        # Live price / stock preview
        preview = QFrame()
        preview.setObjectName("preview")
        preview_layout = QHBoxLayout(preview)
        preview_layout.setContentsMargins(14, 10, 14, 10)
        price_box = QVBoxLayout()
        price_box.setSpacing(0)
        price_caption = QLabel("Prix du verre")
        price_caption.setObjectName("fieldLabel")
        self.lens_price_label = QLabel("—")
        self.lens_price_label.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {TEXT};")
        price_box.addWidget(price_caption)
        price_box.addWidget(self.lens_price_label)
        self.lens_stock_label = QLabel("")
        self.lens_stock_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lens_stock_label.setWordWrap(True)
        preview_layout.addLayout(price_box)
        preview_layout.addStretch()
        preview_layout.addWidget(self.lens_stock_label)
        grid.addWidget(preview, 9, 0, 1, 2)

        self.add_lens_btn = QPushButton("Ajouter au panier")
        self.add_lens_btn.setObjectName("primary")
        self.add_lens_btn.setCursor(Qt.PointingHandCursor)
        self.add_lens_btn.clicked.connect(self.add_lens_to_cart)
        grid.addWidget(self.add_lens_btn, 10, 0, 1, 2)

        grid.setRowStretch(11, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        return page
    
    def _build_contact_lens_page(self):
        """Contact lens page with type filter + searchable list."""
        page = make_plain(QWidget())
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Type filter dropdown
        type_label = QLabel("Type de lentille")
        type_label.setObjectName("fieldLabel")
        layout.addWidget(type_label)

        self.cl_type = QComboBox()
        self.cl_type.setObjectName("field")
        self.cl_type.addItems(CONTACT_LENS_TYPES)
        self.cl_type.currentTextChanged.connect(self.load_contact_lenses)
        layout.addWidget(self.cl_type)

        # Searchable list
        self.cl_picker = ItemPicker("Rechercher une lentille de contact...")
        self.cl_picker.add_requested.connect(self.add_inventory_item)
        layout.addWidget(self.cl_picker, 1)

        return page
    
    def _build_repair_page(self):
        """Custom form for repairs and services (manual description + price)."""
        page = make_plain(QWidget())
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        def field_label(text):
            label = QLabel(text)
            label.setObjectName("fieldLabel")
            return label

        layout.addWidget(field_label("Description du service"))

        self.repair_desc = QLineEdit()
        self.repair_desc.setObjectName("field")
        self.repair_desc.setPlaceholderText("Ex: Soudure monture, changement verres...")
        layout.addWidget(self.repair_desc)

        layout.addWidget(field_label("Prix du service (DA)"))

        from PySide6.QtWidgets import QDoubleSpinBox
        self.repair_price = QDoubleSpinBox()
        self.repair_price.setObjectName("field")
        self.repair_price.setRange(0, 999999)
        self.repair_price.setSuffix(" DA")
        self.repair_price.setSingleStep(100)
        layout.addWidget(self.repair_price)

        layout.addStretch()

        self.add_repair_btn = QPushButton("Ajouter au panier")
        self.add_repair_btn.setObjectName("primary")
        self.add_repair_btn.setCursor(Qt.PointingHandCursor)
        self.add_repair_btn.clicked.connect(self.add_repair_to_cart)
        layout.addWidget(self.add_repair_btn)

        return page

    # --------------------------------------------------------
    # PATIENT
    # --------------------------------------------------------
    def _on_patient_text_changed(self, text):
        self.selected_patient_id = parse_patient_id(text)
        self._update_patient_status()
        # A completed "Nom Prénom (ID: n)" entry doesn't need another search (avoids the popup re-opening)
        if self.selected_patient_id is None:
            self.update_patient_search(text)

    def _update_patient_status(self):
        if self.selected_patient_id is not None:
            text, color = "Patient sélectionné", SUCCESS
        elif self.patient_search.text().strip():
            text, color = "Choisissez un patient dans la liste", WARNING
        else:
            text, color = "Aucun patient sélectionné", MUTED
        self.patient_status.setText(text)
        self.patient_status.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 600;")

    def update_patient_search(self, text):
        if len(text) < 1:
            self.selected_patient_id = None
            return

        patients = PatientModel.get_all_patients(text)
        names = []
        self.patient_map = {}

        for p in patients:
            display_name = f"{p['nom']} {p['prenom']} (ID: {p['id']})"
            names.append(display_name)
            self.patient_map[display_name] = p['id']

        self.patient_completer.setModel(QStringListModel(names))

        if names:
            self.patient_completer.complete()

    def on_patient_selected(self, text):
        self.selected_patient_id = parse_patient_id(text)
        self._update_patient_status()

    # --------------------------------------------------------
    # DATA LOADING
    # --------------------------------------------------------
    def load_inventory_items(self):
        from models.inventory_model import CONTACT_LENS_TYPES
        items = [i for i in InventoryModel.get_all_items()
                 if i['category'] not in CONTACT_LENS_TYPES 
                 and i['category'] != 'Lunettes de Soleil']
        self.frame_picker.set_items(items)

    def load_contact_lenses(self):
        if not hasattr(self, 'cl_type'):
            return
        cl_type = self.cl_type.currentText()
        if cl_type:
            self.cl_picker.set_items(InventoryModel.get_items_by_category(cl_type))

    def load_sunglasses(self):
        self.sun_picker.set_items(InventoryModel.get_items_by_category("Lunettes de Soleil"))

    def load_treatments(self):
        """Dynamically loads all treatment columns from the Lens Matrix."""
        self.lens_treatment.clear()
        self.lens_treatment.addItems(LensModel.get_all_treatments())

    def update_lens_groups(self, *_):
        lens_type = self.lens_type.currentText()
        lenses = LensModel.get_lenses(lens_type)
        groups = list(dict.fromkeys([l['optical_group'] for l in lenses]))

        self.lens_group.clear()
        self.lens_group.addItems(groups)
        self.refresh_lens_preview()

    def update_lens_sph_cyl_options(self, *_):
        """Updates SPH/CYL dropdowns with valid values for the selected group."""
        group_name = self.lens_group.currentText()

        self.lens_sph.blockSignals(True)
        self.lens_cyl.blockSignals(True)
        self.lens_sph.clear()
        self.lens_cyl.clear()

        if group_name:
            sph_vals, cyl_vals = LensModel.get_valid_values_for_group(group_name)
            for value, display in sph_vals:
                self.lens_sph.addItem(f"{display} D", value)
            for value, display in cyl_vals:
                self.lens_cyl.addItem(f"{display} D", value)
            # Group without a cylinder suffix (e.g. G2) only allows 0
            self.lens_cyl.setEnabled(len(cyl_vals) > 1)

        self.lens_sph.blockSignals(False)
        self.lens_cyl.blockSignals(False)
        self.refresh_lens_preview()

    def showEvent(self, event):
        super().showEvent(event)
        if not event.spontaneous():
            self.load_inventory_items()
            self.load_contact_lenses()
            self.load_sunglasses()  # 
            self.refresh_cart()

    # --------------------------------------------------------
    # LENS PREVIEW
    # --------------------------------------------------------
    def _current_lens(self):
        group = self.lens_group.currentText()
        treatment = self.lens_treatment.currentText()
        if not group or not treatment:
            return None
        query = "SELECT id, retail_price FROM lenses WHERE type=? AND optical_group=? AND treatment=?"
        try:
            return db.fetch_one(query, (self.lens_type.currentText(), group, treatment))
        except Exception:
            return None

    def refresh_lens_preview(self, *_):
        if not hasattr(self, "add_lens_btn"):
            return

        sph = self.lens_sph.currentData()
        cyl = self.lens_cyl.currentData()
        lens = self._current_lens()

        def show(price, message, color, can_add):
            self.lens_price_label.setText(price)
            self.lens_stock_label.setText(message)
            self.lens_stock_label.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 600;")
            self.add_lens_btn.setEnabled(can_add)

        if not lens or lens['retail_price'] <= 0:
            show("—", "Prix non défini dans la matrice", WARNING, False)
            return
        if sph is None or cyl is None:
            show(fmt_da(lens['retail_price']), "Choisissez SPH et CYL", MUTED, False)
            return

        try:
            from models.lens_stock_model import LensStockModel
            available = LensStockModel.get_stock_for_combo(lens['id'], sph, cyl)
        except Exception:
            show(fmt_da(lens['retail_price']), "", MUTED, True)
            return

        remaining = available - self._lens_in_cart(lens['id'], sph, cyl)
        if remaining <= 0:
            show(fmt_da(lens['retail_price']), "Rupture de stock pour cette correction", DANGER, False)
        elif remaining <= 3:
            show(fmt_da(lens['retail_price']), f"Stock faible : {remaining}", WARNING, True)
        else:
            show(fmt_da(lens['retail_price']), f"En stock : {remaining}", SUCCESS, True)

    def _lens_in_cart(self, lens_id, sph, cyl):
        return sum(1 for item in self.cart_items
                   if item.get('lens_id') == lens_id and item.get('sph') == sph and item.get('cyl') == cyl)

    # --------------------------------------------------------
    # CART ACTIONS
    # --------------------------------------------------------
    def get_cart_count(self, item_id, item_type="inventory", sph=None, cyl=None):
        """Counts how many of a specific item are already in the cart."""
        count = 0
        for item in self.cart_items:
            if item_type == "inventory" and item.get('inventory_id') == item_id:
                count += 1
            elif item_type == "lens" and item.get('lens_id') == item_id:
                if sph is not None and cyl is not None:
                    if item.get('sph') == sph and item.get('cyl') == cyl:
                        count += 1
                else:
                    count += 1
        return count

    def add_inventory_item(self, item_data):
        """Adds a frame / accessory / contact lens coming from inventory."""
        in_cart = self.get_cart_count(item_data['id'], "inventory")
        if item_data['stock_qty'] - in_cart <= 0:
            QMessageBox.warning(self, "Rupture de Stock", f"Stock insuffisant pour '{item_data['name']}'.")
            return

        self.cart_items.append({
            'type': item_data['category'],
            'description': item_data['name'],
            'price': item_data['retail_price'],
            'discount': 0.0,
            'inventory_id': item_data['id']
        })
        self.refresh_cart()

    def add_lens_to_cart(self):
        lens_type = self.lens_type.currentText()
        group = self.lens_group.currentText()
        treatment = self.lens_treatment.currentText()
        vision = self.lens_vision.currentText()
        sph = self.lens_sph.currentData()
        cyl = self.lens_cyl.currentData()

        if sph is None or cyl is None:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner SPH et CYL.")
            return

        lens = self._current_lens()
        if not lens or lens['retail_price'] <= 0:
            QMessageBox.warning(self, "Prix Manquant",
                                "Le prix de ce verre n'est pas défini dans la matrice ou est égal à 0.")
            return

        from models.lens_stock_model import LensStockModel
        available = LensStockModel.get_stock_for_combo(lens['id'], sph, cyl)
        in_cart = self._lens_in_cart(lens['id'], sph, cyl)

        if available - in_cart <= 0:
            QMessageBox.warning(self, "Rupture de Stock",
                                f"Stock insuffisant pour SPH {fmt_sign(sph)} / CYL {fmt_sign(cyl)}.\n"
                                f"Stock total: {available}\nDans le panier: {in_cart}")
            return

        description = (f"Verre {vision} {lens_type} {treatment} ({group}) "
                       f"SPH:{fmt_sign(sph)} CYL:{fmt_sign(cyl)}")

        self.cart_items.append({
            'type': 'Verre',
            'description': description,
            'price': lens['retail_price'],
            'discount': 0.0,
            'lens_id': lens['id'],
            'sph': sph,
            'cyl': cyl
        })
        self.refresh_cart()
    
    def add_repair_to_cart(self):
        desc = self.repair_desc.text().strip()
        price = self.repair_price.value()

        if not desc:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une description.")
            return
        if price <= 0:
            QMessageBox.warning(self, "Erreur", "Le prix doit être supérieur à 0.")
            return

        self.cart_items.append({
            'type': 'Service',
            'description': desc,
            'price': price,
            'discount': 0.0
        })
        self.refresh_cart()
        self.repair_desc.clear()
        self.repair_price.setValue(0)

    def remove_item_from_cart(self, row_index):
        if 0 <= row_index < len(self.cart_items):
            del self.cart_items[row_index]
            self.refresh_cart()

    def clear_cart(self):
        if not self.cart_items:
            return
        answer = QMessageBox.question(self, "Vider le panier",
                                      "Supprimer tous les articles du panier ?")
        if answer == QMessageBox.Yes:
            self.cart_items = []
            self.refresh_cart()

    def _type_badge(self, type_name):
        bg, fg = TYPE_BADGES.get(type_name, DEFAULT_BADGE)
        wrapper = make_plain(QWidget())
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(8, 0, 8, 0)
        badge = QLabel(str(type_name))
        badge.setStyleSheet(f"background: {bg}; color: {fg}; border-radius: 9px; "
                            f"padding: 3px 10px; font-size: 11px; font-weight: 700;")
        badge.setMinimumWidth(64)
        badge.setAlignment(Qt.AlignCenter)
        layout.addWidget(badge, 0, Qt.AlignLeft | Qt.AlignVCenter)
        return wrapper

    def refresh_cart(self):
        count = len(self.cart_items)
        self.cart_stack.setCurrentIndex(1 if count else 0)
        self.cart_table.clearContents()
        self.cart_table.setRowCount(count)

        right_center = Qt.AlignRight | Qt.AlignVCenter

        for row, item in enumerate(self.cart_items):
            self.cart_table.setCellWidget(row, 0, self._type_badge(item['type']))

            desc = QTableWidgetItem(item['description'])
            desc.setToolTip(item['description'])
            self.cart_table.setItem(row, 1, desc)

            price = QTableWidgetItem(fmt_num(item['price']))
            price.setTextAlignment(right_center)
            self.cart_table.setItem(row, 2, price)

            discount_value = item.get('discount', 0.0)
            discount = QTableWidgetItem(fmt_num(discount_value) if discount_value else "—")
            discount.setTextAlignment(right_center)
            if not discount_value:
                discount.setForeground(QColor("#9CA3AF"))
            self.cart_table.setItem(row, 3, discount)

            remove_btn = QPushButton("✕")
            remove_btn.setObjectName("removeBtn")
            remove_btn.setFixedSize(30, 30)
            remove_btn.setToolTip("Retirer du panier")
            remove_btn.setCursor(Qt.PointingHandCursor)
            remove_btn.clicked.connect(lambda checked=False, r=row: self.remove_item_from_cart(r))
            holder = make_plain(QWidget())
            holder_layout = QHBoxLayout(holder)
            holder_layout.setContentsMargins(0, 0, 8, 0)
            holder_layout.addWidget(remove_btn, 0, Qt.AlignCenter)
            self.cart_table.setCellWidget(row, 4, holder)

        subtotal = sum(i['price'] for i in self.cart_items)
        discounts = sum(i.get('discount', 0.0) for i in self.cart_items)
        total = subtotal - discounts

        self.count_pill.setText(str(count))
        self.clear_btn.setVisible(count > 0)
        self.subtotal_label.setText(fmt_da(subtotal))
        self.discount_label.setText(f"- {fmt_da(discounts)}")
        self.discount_row.setVisible(discounts > 0)
        self.total_label.setText(fmt_da(total))
        self.checkout_btn.setEnabled(count > 0)

        # Keep the inventory lists and lens preview in sync with what is already in the cart
        counts = {}
        for item in self.cart_items:
            if 'inventory_id' in item:
                counts[item['inventory_id']] = counts.get(item['inventory_id'], 0) + 1
        self.frame_picker.set_cart_counts(counts)
        self.cl_picker.set_cart_counts(counts)
        self.sun_picker.set_cart_counts(counts)
        self.refresh_lens_preview()

    # --------------------------------------------------------
    # CHECKOUT / DEBTS
    # --------------------------------------------------------
    def open_settlement(self):
        if not self.cart_items:
            QMessageBox.warning(self, "Panier Vide", "Veuillez ajouter des articles avant de finaliser.")
            return

        patient_id = parse_patient_id(self.patient_search.text())
        if not patient_id:
            QMessageBox.warning(self, "Patient Manquant",
                                "Veuillez sélectionner un patient valide dans la liste de recherche.")
            self.patient_search.setFocus()
            return

        dialog = SettlementDialog(patient_id, self.cart_items, self)
        if dialog.exec():
            self.cart_items = []
            self.patient_search.clear()

            self.load_inventory_items()
            self.load_contact_lenses()
            self.load_sunglasses() 
            self.update_lens_groups()
            self.refresh_cart()

            app = QApplication.instance()
            app.catalogue_dirty = True
            app.finance_dirty = True

    def open_pending_orders(self):
        """Opens the pending orders dialog for debt settlement."""
        dialog = PendingOrdersDialog(self)
        dialog.exec()
        # Refresh lists in case stock changed (safety)
        self.load_inventory_items()
        self.load_contact_lenses()
        self.load_sunglasses() 
        self.refresh_cart()