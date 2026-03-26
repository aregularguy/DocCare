"""Main application window with sidebar navigation."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QStackedWidget, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from .styles import get_stylesheet, NAV_ICONS, COLORS


class NavigationButton(QPushButton):
    """Custom navigation button for sidebar."""

    def __init__(self, icon: str, text: str, parent=None):
        super().__init__(parent)
        self.setObjectName("nav_button")
        self.icon = icon
        self.button_text = text
        self.setText(f"  {icon}  {text}")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(44)
        self.setProperty("active", False)

    def set_active(self, active: bool):
        """Set button active state."""
        self.setProperty("active", active)
        self.style().unpolish(self)
        self.style().polish(self)


class Sidebar(QWidget):
    """Sidebar navigation widget (Cursor-style)."""

    navigation_changed = pyqtSignal(str)  # Emits the page name

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(240)
        self.active_button = None
        self.buttons = {}
        self.init_ui()

    def init_ui(self):
        """Initialize the sidebar UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header section
        header = self.create_header()
        layout.addWidget(header)

        # Navigation buttons
        nav_container = QWidget()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(12, 12, 12, 12)
        nav_layout.setSpacing(4)

        # First group (3 items)
        self.add_nav_button(nav_layout, 'dashboard', 'Dashboard')
        self.add_nav_button(nav_layout, 'patients', 'Patients')
        self.add_nav_button(nav_layout, 'treatments', 'Treatments')

        # Separator
        nav_layout.addWidget(self.create_separator())

        # Second group (3 items)
        self.add_nav_button(nav_layout, 'payments', 'Payments')
        self.add_nav_button(nav_layout, 'prescriptions', 'Prescriptions')
        self.add_nav_button(nav_layout, 'analytics', 'Analytics')

        # Separator
        nav_layout.addWidget(self.create_separator())

        # Additional options
        self.add_nav_button(nav_layout, 'settings', 'Settings')
        self.add_nav_button(nav_layout, 'export', 'Export Data')

        nav_layout.addStretch()

        # Wrap in scroll area
        scroll = QScrollArea()
        scroll.setWidget(nav_container)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        layout.addWidget(scroll)

        # Set first button as active
        if 'dashboard' in self.buttons:
            self.set_active_page('dashboard')

    def create_header(self):
        """Create sidebar header with app title."""
        header = QFrame()
        header.setObjectName("sidebar_header")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 20, 20, 20)

        # App title
        title = QLabel("🦷 DentNest")
        title.setObjectName("app_title")
        title_font = QFont("Segoe UI", 16, QFont.Weight.Bold)
        title.setFont(title_font)
        header_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Dental Practice Manager")
        subtitle.setObjectName("app_subtitle")
        subtitle.setStyleSheet(f"color: {COLORS['text_secondary']};")
        header_layout.addWidget(subtitle)

        return header

    def create_separator(self):
        """Create a horizontal separator line."""
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(1)
        return separator

    def add_nav_button(self, layout, key: str, text: str):
        """Add a navigation button to the layout."""
        icon = NAV_ICONS.get(key, '•')
        button = NavigationButton(icon, text)
        button.clicked.connect(lambda: self.on_nav_clicked(key))
        self.buttons[key] = button
        layout.addWidget(button)

    def on_nav_clicked(self, page_name: str):
        """Handle navigation button click."""
        self.set_active_page(page_name)
        self.navigation_changed.emit(page_name)

    def set_active_page(self, page_name: str):
        """Set the active navigation button."""
        # Deactivate previous button
        if self.active_button:
            self.active_button.set_active(False)

        # Activate new button
        if page_name in self.buttons:
            button = self.buttons[page_name]
            button.set_active(True)
            self.active_button = button


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DentNest - Dental Practice Management")
        self.setMinimumSize(1280, 800)
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        """Initialize the main window UI."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.navigation_changed.connect(self.on_navigation_changed)
        main_layout.addWidget(self.sidebar)

        # Content area
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("content_area")
        main_layout.addWidget(self.content_area)

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
