"""Analytics dashboard with charts (Cursor-style)."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QComboBox, QGridLayout
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from ...services.analytics_service import AnalyticsService
from ...utils.formatters import format_currency


class ChartWidget(QFrame):
    """Widget for displaying a matplotlib chart."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.title = title
        self.init_ui()

    def init_ui(self):
        """Initialize the chart widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel(self.title)
        title_label.setObjectName("section_title")
        layout.addWidget(title_label)

        # Create matplotlib figure
        self.figure = Figure(figsize=(6, 4), dpi=100, facecolor='#FFFFFF')
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)

    def clear(self):
        """Clear the chart."""
        self.figure.clear()
        self.canvas.draw()


class AnalyticsDashboardWidget(QWidget):
    """Analytics dashboard with charts and metrics."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.analytics_service = AnalyticsService()
        self.init_ui()

    def init_ui(self):
        """Initialize the analytics dashboard UI."""
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

        # Header with period selector
        header_layout = QHBoxLayout()

        title = QLabel("Analytics")
        title.setObjectName("page_title")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Period selector
        period_label = QLabel("Period:")
        period_label.setStyleSheet("font-weight: 500; margin-right: 8px;")
        header_layout.addWidget(period_label)

        self.period_selector = QComboBox()
        self.period_selector.addItems(["Today", "This Week", "This Month", "This Year"])
        self.period_selector.setCurrentText("This Month")
        self.period_selector.currentTextChanged.connect(self.on_period_changed)
        self.period_selector.setMinimumWidth(150)
        header_layout.addWidget(self.period_selector)

        main_layout.addLayout(header_layout)

        # Metrics cards
        self.metrics_grid = self.create_metrics_grid()
        main_layout.addWidget(self.metrics_grid)

        # Charts grid
        charts_grid = QGridLayout()
        charts_grid.setSpacing(16)

        # Payment trends chart (line chart)
        self.payment_chart = ChartWidget("Payment Trends")
        charts_grid.addWidget(self.payment_chart, 0, 0, 1, 2)

        # Treatment types chart (donut chart)
        self.treatment_chart = ChartWidget("Treatment Distribution")
        charts_grid.addWidget(self.treatment_chart, 1, 0)

        # Payment methods chart (donut chart)
        self.payment_method_chart = ChartWidget("Payment Methods")
        charts_grid.addWidget(self.payment_method_chart, 1, 1)

        # Top medicines chart (bar chart)
        self.medicine_chart = ChartWidget("Top Prescribed Medicines")
        charts_grid.addWidget(self.medicine_chart, 2, 0, 1, 2)

        main_layout.addLayout(charts_grid)

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
        from .dashboard import MetricCard

        grid = QFrame()
        layout = QGridLayout(grid)
        layout.setSpacing(16)

        # Create metric cards
        self.total_patients_metric = MetricCard("Total Patients", "0")
        self.new_patients_metric = MetricCard("New Patients", "0")
        self.total_payments_metric = MetricCard("Total Payments", "₹0")
        self.treatments_metric = MetricCard("Treatments", "0")

        # Add to grid
        layout.addWidget(self.total_patients_metric, 0, 0)
        layout.addWidget(self.new_patients_metric, 0, 1)
        layout.addWidget(self.total_payments_metric, 0, 2)
        layout.addWidget(self.treatments_metric, 0, 3)

        return grid

    def on_period_changed(self, text: str):
        """Handle period selector change."""
        self.refresh_data()

    def get_period_key(self):
        """Get period key from selector."""
        text = self.period_selector.currentText()
        mapping = {
            "Today": "today",
            "This Week": "week",
            "This Month": "month",
            "This Year": "year"
        }
        return mapping.get(text, "month")

    def refresh_data(self):
        """Refresh all analytics data and charts."""
        period = self.get_period_key()
        dashboard_data = self.analytics_service.get_dashboard_data(period)

        # Update metrics
        self.update_metrics(dashboard_data)

        # Update charts
        self.update_payment_trends(dashboard_data)
        self.update_treatment_distribution(dashboard_data)
        self.update_payment_methods(dashboard_data)
        self.update_medicine_stats(dashboard_data)

    def update_metrics(self, data: dict):
        """Update metric cards."""
        patients = data['patients']
        payments = data['payments']
        treatments = data['treatments']

        self.total_patients_metric.update_value(str(patients['total_patients']))
        self.new_patients_metric.update_value(str(patients['new_patients']))
        self.total_payments_metric.update_value(format_currency(payments['total_amount']))
        self.treatments_metric.update_value(str(treatments['treatment_count']))

    def update_payment_trends(self, data: dict):
        """Update payment trends line chart."""
        self.payment_chart.figure.clear()
        ax = self.payment_chart.figure.add_subplot(111)

        # Get daily payments
        start_date = data['start_date']
        end_date = data['end_date']

        from datetime import datetime
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()

        daily_payments = self.analytics_service.get_daily_payments(start, end)

        if daily_payments:
            dates = [datetime.fromisoformat(d['date']) for d in daily_payments]
            amounts = [d['amount'] for d in daily_payments]

            ax.plot(dates, amounts, color='#007AFF', linewidth=2.5, marker='o', markersize=4)
            ax.fill_between(dates, amounts, alpha=0.2, color='#007AFF')
            ax.set_xlabel('Date', fontsize=10, color='#1D1D1F')
            ax.set_ylabel('Amount (₹)', fontsize=10, color='#1D1D1F')
            ax.grid(True, alpha=0.2, linestyle='--')
            ax.tick_params(colors='#1D1D1F', labelsize=9)
        else:
            ax.text(0.5, 0.5, 'No payment data available',
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=12, color='#86868B')

        self.payment_chart.figure.tight_layout()
        self.payment_chart.canvas.draw()

    def update_treatment_distribution(self, data: dict):
        """Update treatment distribution donut chart (Cursor-style)."""
        self.treatment_chart.figure.clear()
        ax = self.treatment_chart.figure.add_subplot(111)

        treatment_types = data['treatments']['treatment_types']

        if treatment_types:
            labels = [t['name'] for t in treatment_types]
            sizes = [t['count'] for t in treatment_types]

            # Cursor-style colors
            colors = ['#007AFF', '#34C759', '#FF9500', '#FF3B30', '#5856D6', '#00C7BE']

            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=labels,
                autopct='%1.1f%%',
                colors=colors[:len(labels)],
                startangle=90,
                pctdistance=0.85,
                wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2)
            )

            # Style text
            for text in texts:
                text.set_color('#1D1D1F')
                text.set_fontsize(10)
                text.set_fontweight('500')

            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(9)
                autotext.set_fontweight('600')

            ax.axis('equal')
        else:
            ax.text(0.5, 0.5, 'No treatment data available',
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=12, color='#86868B')
            ax.axis('off')

        self.treatment_chart.figure.tight_layout()
        self.treatment_chart.canvas.draw()

    def update_payment_methods(self, data: dict):
        """Update payment methods donut chart (Cursor-style)."""
        self.payment_method_chart.figure.clear()
        ax = self.payment_method_chart.figure.add_subplot(111)

        payment_methods = data['payments']['payment_methods']

        if payment_methods:
            labels = [m['method'].capitalize() for m in payment_methods]
            sizes = [m['total'] for m in payment_methods]

            colors = ['#34C759', '#007AFF', '#FF9500', '#5856D6', '#FF3B30']

            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=labels,
                autopct='%1.1f%%',
                colors=colors[:len(labels)],
                startangle=90,
                pctdistance=0.85,
                wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2)
            )

            for text in texts:
                text.set_color('#1D1D1F')
                text.set_fontsize(10)
                text.set_fontweight('500')

            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(9)
                autotext.set_fontweight('600')

            ax.axis('equal')
        else:
            ax.text(0.5, 0.5, 'No payment data available',
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=12, color='#86868B')
            ax.axis('off')

        self.payment_method_chart.figure.tight_layout()
        self.payment_method_chart.canvas.draw()

    def update_medicine_stats(self, data: dict):
        """Update medicine statistics bar chart."""
        self.medicine_chart.figure.clear()
        ax = self.medicine_chart.figure.add_subplot(111)

        medicine_stats = data['prescriptions']['medicine_stats']

        if medicine_stats:
            # Take top 10
            top_medicines = sorted(medicine_stats, key=lambda x: x['count'], reverse=True)[:10]
            medicines = [m['medicine'] for m in top_medicines]
            counts = [m['count'] for m in top_medicines]

            bars = ax.barh(medicines, counts, color='#007AFF', height=0.6)

            # Add value labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                       f'{int(width)}',
                       ha='left', va='center', fontsize=9, color='#1D1D1F', fontweight='500')

            ax.set_xlabel('Prescription Count', fontsize=10, color='#1D1D1F')
            ax.tick_params(colors='#1D1D1F', labelsize=9)
            ax.grid(True, alpha=0.2, axis='x', linestyle='--')
        else:
            ax.text(0.5, 0.5, 'No prescription data available',
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=12, color='#86868B')
            ax.axis('off')

        self.medicine_chart.figure.tight_layout()
        self.medicine_chart.canvas.draw()
