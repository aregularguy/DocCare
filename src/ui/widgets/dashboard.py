"""Dashboard widget - Home screen with quick stats."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt
from datetime import date
from ...services.analytics_service import AnalyticsService
from ...services.patient_service import PatientService
from ...utils.formatters import format_currency


class MetricCard(QFrame):
    """Card widget for displaying a single metric."""

    def __init__(self, title: str, value: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("metric_card")
        # Global QSS pads metric cards; the layout margins already provide spacing
        self.setStyleSheet("QFrame#metric_card { padding:0px; }")
        self.init_ui(title, value, subtitle)

    def init_ui(self, title: str, value: str, subtitle: str):
        """Initialize the metric card UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Value (large number)
        value_label = QLabel(value)
        value_label.setObjectName("metric_value")
        layout.addWidget(value_label)

        # Title
        title_label = QLabel(title)
        title_label.setObjectName("metric_label")
        layout.addWidget(title_label)

        # Subtitle (optional)
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("color: #5B6B73; font-size: 11px;")
            layout.addWidget(subtitle_label)

    def update_value(self, value: str):
        """Update the metric value."""
        value_label = self.findChild(QLabel, "metric_value")
        if value_label:
            value_label.setText(value)


class DashboardWidget(QWidget):
    """Dashboard home screen widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.analytics_service = AnalyticsService()
        self.patient_service = PatientService()
        self.init_ui()

    def init_ui(self):
        """Initialize the dashboard UI."""
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Container widget
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(32)

        # Page title
        title = QLabel("Dashboard")
        title.setObjectName("page_title")
        main_layout.addWidget(title)

        # Today's date
        today_label = QLabel(f"Today: {date.today().strftime('%A, %B %d, %Y')}")
        today_label.setStyleSheet("color: #5B6B73; font-size: 14px;")
        main_layout.addWidget(today_label)

        # Metrics grid
        self.metrics_grid = self.create_metrics_grid()
        main_layout.addWidget(self.metrics_grid)

        # Recent activity section
        recent_section = self.create_recent_activity_section()
        main_layout.addWidget(recent_section)

        # Quick actions section
        quick_actions = self.create_quick_actions_section()
        main_layout.addWidget(quick_actions)

        main_layout.addStretch()

        scroll.setWidget(container)

        # Set main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

        # Load initial data
        self.refresh_data()

    def create_metrics_grid(self):
        """Create the metrics grid with cards."""
        grid = QFrame()
        layout = QGridLayout(grid)
        layout.setSpacing(16)

        # Create metric cards
        self.total_patients_card = MetricCard("Total Patients", "0")
        self.new_patients_card = MetricCard("New Today", "0")
        self.payments_today_card = MetricCard("Payments Today", format_currency(0))
        self.pending_payments_card = MetricCard("Pending Payments", format_currency(0))

        # Add to grid
        layout.addWidget(self.total_patients_card, 0, 0)
        layout.addWidget(self.new_patients_card, 0, 1)
        layout.addWidget(self.payments_today_card, 0, 2)
        layout.addWidget(self.pending_payments_card, 0, 3)

        return grid

    def create_recent_activity_section(self):
        """Create recent activity section."""
        section = QFrame()
        section.setObjectName("card")
        layout = QVBoxLayout(section)

        # Section title
        title = QLabel("Recent Activity")
        title.setObjectName("section_title")
        layout.addWidget(title)

        # Activity list (placeholder)
        activity_label = QLabel("No recent activity")
        activity_label.setStyleSheet("color: #5B6B73; padding: 20px; font-size: 14px;")
        activity_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(activity_label)

        return section

    def create_quick_actions_section(self):
        """Create quick actions section."""
        section = QFrame()
        layout = QVBoxLayout(section)

        # Section title
        title = QLabel("Quick Actions")
        title.setObjectName("section_title")
        layout.addWidget(title)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        from PyQt6.QtWidgets import QPushButton

        # Quick action buttons
        add_patient_btn = QPushButton("➕ Add Patient")
        add_patient_btn.setObjectName("primary_button")
        add_patient_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_patient_btn.clicked.connect(self.on_add_patient_clicked)
        buttons_layout.addWidget(add_patient_btn)

        add_treatment_btn = QPushButton("🦷 New Treatment")
        add_treatment_btn.setObjectName("secondary_button")
        add_treatment_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_treatment_btn.clicked.connect(self.on_new_treatment_clicked)
        buttons_layout.addWidget(add_treatment_btn)

        record_payment_btn = QPushButton("💰 Record Payment")
        record_payment_btn.setObjectName("secondary_button")
        record_payment_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        record_payment_btn.clicked.connect(self.on_record_payment_clicked)
        buttons_layout.addWidget(record_payment_btn)

        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

        return section

    def refresh_data(self):
        """Refresh dashboard data."""
        # Get today's analytics
        dashboard_data = self.analytics_service.get_dashboard_data('today')

        # Update metrics
        patients_data = dashboard_data['patients']
        self.total_patients_card.update_value(str(patients_data['total_patients']))
        self.new_patients_card.update_value(str(patients_data['new_patients']))

        payments_data = dashboard_data['payments']
        self.payments_today_card.update_value(format_currency(payments_data['total_amount']))

        treatments_data = dashboard_data['treatments']
        self.pending_payments_card.update_value(format_currency(treatments_data['pending_amount']))

    def on_add_patient_clicked(self):
        """Navigate to patients page to add new patient."""
        # Get main window and navigate to patients page
        main_window = self.window()
        if hasattr(main_window, 'sidebar'):
            main_window.sidebar.on_nav_clicked('patients')

    def on_new_treatment_clicked(self):
        """Navigate to treatments page to add new treatment."""
        main_window = self.window()
        if hasattr(main_window, 'sidebar'):
            main_window.sidebar.on_nav_clicked('treatments')

    def on_record_payment_clicked(self):
        """Navigate to payments page to record payment."""
        main_window = self.window()
        if hasattr(main_window, 'sidebar'):
            main_window.sidebar.on_nav_clicked('payments')
