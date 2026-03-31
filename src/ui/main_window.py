"""Main application window with sidebar navigation."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QStackedWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
import os
from .styles import get_stylesheet, NAV_ICONS, COLORS

_BG = COLORS['sidebar_bg']
_HOVER = COLORS['sidebar_hover']
_ACTIVE = COLORS['sidebar_active']
_ACTIVE_TEXT = COLORS['sidebar_text']
_DIM_TEXT = COLORS['sidebar_text_secondary']
_ACCENT = COLORS['sidebar_active_border']


class NavItem(QWidget):
    """Vertical icon + label nav item — TatvaPractice style."""

    clicked_signal = pyqtSignal()

    def __init__(self, icon: str, text: str, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(70)
        self._active = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 10, 4, 10)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_lbl = QLabel(icon)
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_lbl.setStyleSheet(f"font-size: 22px; background: transparent; color: white;")

        self.text_lbl = QLabel(text)
        self.text_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_lbl.setWordWrap(True)
        self.text_lbl.setStyleSheet(
            f"font-size: 10px; font-weight: 500; background: transparent; color: {_DIM_TEXT};"
        )

        layout.addWidget(self.icon_lbl)
        layout.addWidget(self.text_lbl)

        self._set_bg(_BG)

    def _set_bg(self, color: str):
        self.setStyleSheet(
            f"QWidget {{ background-color: {color}; border-radius: 10px; }}"
        )

    def set_active(self, active: bool):
        self._active = active
        if active:
            self._set_bg(_ACTIVE)
            self.text_lbl.setStyleSheet(
                f"font-size: 10px; font-weight: 700; background: transparent; color: {_ACTIVE_TEXT};"
            )
        else:
            self._set_bg(_BG)
            self.text_lbl.setStyleSheet(
                f"font-size: 10px; font-weight: 500; background: transparent; color: {_DIM_TEXT};"
            )

    def mousePressEvent(self, event):
        self.clicked_signal.emit()

    def enterEvent(self, event):
        if not self._active:
            self._set_bg(_HOVER)

    def leaveEvent(self, event):
        if not self._active:
            self._set_bg(_BG)


class Sidebar(QWidget):
    """Compact icon+label sidebar — TatvaPractice style."""

    navigation_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(86)
        self.active_item = None
        self.items = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._create_header())

        # Nav items container
        nav = QWidget()
        nav.setStyleSheet(f"background-color: {_BG};")
        nav_layout = QVBoxLayout(nav)
        nav_layout.setContentsMargins(8, 12, 8, 12)
        nav_layout.setSpacing(2)

        self._add_item(nav_layout, 'dashboard',    'Dashboard')
        self._add_item(nav_layout, 'patients',     'Patients')
        self._add_item(nav_layout, 'treatments',   'Treatments')
        nav_layout.addWidget(self._separator())
        self._add_item(nav_layout, 'payments',     'Payments')
        self._add_item(nav_layout, 'prescriptions','Prescribe')
        self._add_item(nav_layout, 'analytics',    'Analytics')
        nav_layout.addWidget(self._separator())
        self._add_item(nav_layout, 'settings',     'Settings')
        self._add_item(nav_layout, 'export',       'Export')
        nav_layout.addStretch()

        layout.addWidget(nav)

        if 'dashboard' in self.items:
            self.set_active_page('dashboard')

    def _create_header(self):
        header = QFrame()
        header.setObjectName("sidebar_header")
        header.setFixedHeight(62)
        header.setStyleSheet(
            f"background-color: {_BG}; border-bottom: 1px solid {COLORS['sidebar_border']};"
        )
        hlay = QVBoxLayout(header)
        hlay.setContentsMargins(0, 8, 0, 8)
        hlay.setSpacing(4)
        hlay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Use the PNG icon instead of emoji
        from PyQt6.QtGui import QPixmap
        icon = QLabel()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icons", "dentnest.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon.setPixmap(pixmap)
        else:
            icon.setText("🦷")
            icon.setStyleSheet(f"font-size: 24px; color: white; background: transparent;")

        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl = QLabel("DentNest")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(
            f"font-size: 9px; font-weight: 700; color: {_DIM_TEXT};"
            f" background: transparent; letter-spacing: 1px;"
        )

        hlay.addWidget(icon)
        hlay.addWidget(lbl)
        return header

    def _separator(self):
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {COLORS['sidebar_border']}; border: none;")
        return sep

    def _add_item(self, layout, key: str, label: str):
        icon = NAV_ICONS.get(key, '•')
        item = NavItem(icon, label)
        item.clicked_signal.connect(lambda: self._on_clicked(key))
        self.items[key] = item
        layout.addWidget(item)

    def _on_clicked(self, page_name: str):
        self.set_active_page(page_name)
        self.navigation_changed.emit(page_name)

    def on_nav_clicked(self, page_name: str):
        """Public alias kept for compatibility with other widgets."""
        self._on_clicked(page_name)

    def set_active_page(self, page_name: str):
        if self.active_item:
            self.active_item.set_active(False)
        if page_name in self.items:
            self.active_item = self.items[page_name]
            self.active_item.set_active(True)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DentNest - Dental Practice Management")
        self.setMinimumSize(1280, 800)

        # Set Window Icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icons", "dentnest.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        """Initialize the main window UI."""
        from .widgets.top_navbar import TopNavBar

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Root vertical layout: navbar on top, body below
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.navbar = TopNavBar()
        root_layout.addWidget(self.navbar)

        # Body: sidebar + content area side by side
        body_widget = QWidget()
        main_layout = QHBoxLayout(body_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.navigation_changed.connect(self.on_navigation_changed)
        main_layout.addWidget(self.sidebar)

        self.content_area = QStackedWidget()
        self.content_area.setObjectName("content_area")
        main_layout.addWidget(self.content_area)

        root_layout.addWidget(body_widget)

        # Initialize pages
        self.init_pages()

    def init_pages(self):
        """Initialize all content pages."""
        # Import page widgets here to avoid circular imports
        from .widgets.dashboard import DashboardWidget
        from .widgets.patient_list import PatientListWidget
        from .widgets.treatment_list import TreatmentListWidget
        from .widgets.payment_list import PaymentListWidget
        from .widgets.prescription_list import PrescriptionListWidget
        from .widgets.analytics_dashboard import AnalyticsDashboardWidget
        from .widgets.settings import SettingsWidget
        from .widgets.export_data import ExportDataWidget

        # Create pages
        self.pages = {
            'dashboard': DashboardWidget(),
            'patients': PatientListWidget(),
            'treatments': TreatmentListWidget(),
            'payments': PaymentListWidget(),
            'prescriptions': PrescriptionListWidget(),
            'analytics': AnalyticsDashboardWidget(),
            'settings': SettingsWidget(),
            'export': ExportDataWidget(),
        }

        # Add pages to stacked widget
        for page in self.pages.values():
            self.content_area.addWidget(page)

        # Show dashboard by default
        self.content_area.setCurrentWidget(self.pages['dashboard'])

    def on_navigation_changed(self, page_name: str):
        """Handle navigation change."""
        if page_name in self.pages:
            page_widget = self.pages[page_name]
            self.content_area.setCurrentWidget(page_widget)

            # Refresh page data if it has a refresh method
            if hasattr(page_widget, 'refresh_data'):
                page_widget.refresh_data()

    def apply_styles(self):
        """Apply the stylesheet to the window."""
        self.setStyleSheet(get_stylesheet())
