"""Analytics dashboard — clean, well-sized charts with proper styling."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QGridLayout, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib
matplotlib.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 10,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.25,
    'grid.linestyle': '--',
})

from ...services.analytics_service import AnalyticsService
from ...utils.formatters import format_currency


# ── Palette ──────────────────────────────────────────────────────────────────
COLORS = ['#1F8A9E', '#2E9E6B', '#C98A2E', '#6E72B8', '#D0534F', '#00C7BE', '#FF2D55']
BG = '#FFFFFF'
TEXT = '#1E2B32'
SUBTEXT = '#5B6B73'

METRIC_ACCENTS = ['#1F8A9E', '#2E9E6B', '#C98A2E', '#6E72B8']
METRIC_BG = ['#E3F3F6', '#E6F5EE', '#FBF1E1', '#EEEFF8']
METRIC_ICONS = ['👥', '🆕', '💰', '🦷']


# ── Metric card ──────────────────────────────────────────────────────────────

class MetricCard(QFrame):
    def __init__(self, icon, title, value, accent, bg):
        super().__init__()
        self.setObjectName("metric_card")
        self.setStyleSheet(
            f"QFrame#metric_card {{"
            f"  background:{bg}; border-radius:12px;"
            f"  border-left:4px solid {accent}; padding:0px;"
            f"}}"
        )
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        self.setMinimumHeight(110)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(6)

        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size:20px; background:transparent;")
        top.addWidget(icon_lbl)
        top.addStretch()
        layout.addLayout(top)

        # Font set via stylesheet: the global `* { font-size }` rule overrides setFont()
        self.value_lbl = QLabel(value)
        self.value_lbl.setStyleSheet(
            f"color:{accent}; background:transparent; font-size:20pt; font-weight:700;"
            f" font-family: 'Segoe UI', 'Noto Sans', sans-serif;"
        )
        layout.addWidget(self.value_lbl)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color:{SUBTEXT}; font-size:12px; font-weight:500; background:transparent;")
        layout.addWidget(title_lbl)

    def update_value(self, v):
        self.value_lbl.setText(v)


# ── Chart card ───────────────────────────────────────────────────────────────

class ChartCard(QFrame):
    """Chart container with title and matplotlib canvas."""

    def __init__(self, title: str, figsize=(7, 3.5), parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet(
            "QFrame#card { background:#FFFFFF; border:1px solid #DDE5E8;"
            " border-radius:12px; padding:0px; }"
        )
        self.setMinimumHeight(300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        title_lbl.setStyleSheet("color:#1E2B32; background:transparent;")
        layout.addWidget(title_lbl)

        self.figure = Figure(figsize=figsize, dpi=96, facecolor=BG)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setStyleSheet("background:transparent;")
        layout.addWidget(self.canvas)

    def clear(self):
        self.figure.clear()
        self.canvas.draw()


# ── Period segmented control ──────────────────────────────────────────────────

class PeriodSelector(QFrame):
    def __init__(self, on_change, parent=None):
        super().__init__(parent)
        self.on_change = on_change
        self.periods = ["Today", "This Week", "This Month", "This Year"]
        self.active = "This Month"
        self.buttons = {}
        self.setStyleSheet(
            "QFrame { background:#EEF3F4; border-radius:8px; padding:2px; }"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        for p in self.periods:
            btn = QPushButton(p)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, period=p: self._select(period))
            btn.setStyleSheet(self._btn_style(p == self.active))
            self.buttons[p] = btn
            layout.addWidget(btn)

    def _btn_style(self, active):
        if active:
            return ("QPushButton { background:#FFFFFF; color:#1F8A9E; font-weight:600;"
                    " border-radius:6px; padding:5px 14px; font-size:12px; border:none; }")
        return ("QPushButton { background:transparent; color:#5B6B73; font-weight:400;"
                " border-radius:6px; padding:5px 14px; font-size:12px; border:none; }"
                "QPushButton:hover { color:#1E2B32; }")

    def _select(self, period):
        self.active = period
        for p, btn in self.buttons.items():
            btn.setStyleSheet(self._btn_style(p == period))
            btn.setChecked(p == period)
        self.on_change(period)

    def get_period_key(self):
        return {"Today": "today", "This Week": "week",
                "This Month": "month", "This Year": "year"}.get(self.active, "month")


# ── Main analytics widget ─────────────────────────────────────────────────────

class AnalyticsDashboardWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.analytics_service = AnalyticsService()
        self.init_ui()

    def init_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        main = QVBoxLayout(container)
        main.setContentsMargins(40, 32, 40, 40)
        main.setSpacing(24)

        # ── Header ──
        header = QHBoxLayout()
        title = QLabel("Analytics")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()

        self.period_selector = PeriodSelector(self._on_period_changed)
        header.addWidget(self.period_selector)
        main.addLayout(header)

        # ── Metric cards ──
        metrics_row = QGridLayout()
        metrics_row.setSpacing(16)
        self.m_patients = MetricCard(METRIC_ICONS[0], "Total Patients", "0",
                                     METRIC_ACCENTS[0], METRIC_BG[0])
        self.m_new = MetricCard(METRIC_ICONS[1], "New Patients", "0",
                                METRIC_ACCENTS[1], METRIC_BG[1])
        self.m_payments = MetricCard(METRIC_ICONS[2], "Total Collected", format_currency(0),
                                     METRIC_ACCENTS[2], METRIC_BG[2])
        self.m_treatments = MetricCard(METRIC_ICONS[3], "Treatments", "0",
                                       METRIC_ACCENTS[3], METRIC_BG[3])
        metrics_row.addWidget(self.m_patients, 0, 0)
        metrics_row.addWidget(self.m_new, 0, 1)
        metrics_row.addWidget(self.m_payments, 0, 2)
        metrics_row.addWidget(self.m_treatments, 0, 3)
        main.addLayout(metrics_row)

        # ── Payment trends (full width) ──
        self.chart_trends = ChartCard("💰  Payment Trends", figsize=(12, 3.2))
        main.addWidget(self.chart_trends)

        # ── Two donut charts side by side ──
        donuts_row = QHBoxLayout()
        donuts_row.setSpacing(16)
        self.chart_treatment = ChartCard("🦷  Treatment Distribution", figsize=(5, 3.8))
        self.chart_methods = ChartCard("💳  Payment Methods", figsize=(5, 3.8))
        donuts_row.addWidget(self.chart_treatment)
        donuts_row.addWidget(self.chart_methods)
        main.addLayout(donuts_row)

        # ── Medicines bar chart (full width) ──
        self.chart_medicines = ChartCard("💊  Top Prescribed Medicines", figsize=(12, 3.5))
        main.addWidget(self.chart_medicines)

        main.addStretch()
        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        self.refresh_data()

    # ── Data refresh ──────────────────────────────────────────────────────────

    def _on_period_changed(self, _text):
        self.refresh_data()

    def refresh_data(self):
        period = self.period_selector.get_period_key()
        data = self.analytics_service.get_dashboard_data(period)
        self._update_metrics(data)
        self._draw_trends(data)
        self._draw_treatment_donut(data)
        self._draw_payment_methods(data)
        self._draw_medicines(data)

    def _update_metrics(self, data):
        self.m_patients.update_value(str(data['patients']['total_patients']))
        self.m_new.update_value(str(data['patients']['new_patients']))
        self.m_payments.update_value(format_currency(data['payments']['total_amount']))
        self.m_treatments.update_value(str(data['treatments']['treatment_count']))

    # ── Payment trends line chart ─────────────────────────────────────────────

    def _draw_trends(self, data):
        fig = self.chart_trends.figure
        fig.clear()
        ax = fig.add_subplot(111)
        ax.set_facecolor(BG)
        fig.patch.set_facecolor(BG)

        from datetime import datetime
        start = datetime.fromisoformat(data['start_date']).date()
        end = datetime.fromisoformat(data['end_date']).date()
        daily = self.analytics_service.get_daily_payments(start, end)

        if daily:
            dates = [datetime.fromisoformat(d['date']) for d in daily]
            amounts = [d['amount'] for d in daily]

            ax.plot(dates, amounts, color='#1F8A9E', linewidth=2.5,
                    marker='o', markersize=5, markerfacecolor='white',
                    markeredgewidth=2, markeredgecolor='#1F8A9E', zorder=3)
            ax.fill_between(dates, amounts, alpha=0.12, color='#1F8A9E')

            # Format x-axis dates nicely
            import matplotlib.dates as mdates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
            fig.autofmt_xdate(rotation=30, ha='right')

            ax.set_ylabel('Amount (Rs.)', color=SUBTEXT, fontsize=10)
            ax.yaxis.set_major_formatter(
                matplotlib.ticker.FuncFormatter(lambda x, _: f'Rs.{int(x):,}')
            )
            ax.tick_params(colors=SUBTEXT, labelsize=9)
            ax.spines['left'].set_color('#DDE5E8')
            ax.spines['bottom'].set_color('#DDE5E8')
        else:
            self._empty(ax, "No payment data for this period")

        fig.tight_layout(pad=1.5)
        self.chart_trends.canvas.draw()

    # ── Treatment donut ───────────────────────────────────────────────────────

    def _draw_treatment_donut(self, data):
        fig = self.chart_treatment.figure
        fig.clear()
        fig.patch.set_facecolor(BG)

        treatment_types = data['treatments']['treatment_types']
        if not treatment_types:
            ax = fig.add_subplot(111)
            self._empty(ax, "No treatment data")
            fig.tight_layout(pad=1.2)
            self.chart_treatment.canvas.draw()
            return

        # Split: donut on left, legend on right
        ax = fig.add_axes([0.0, 0.05, 0.55, 0.9])
        ax.set_facecolor(BG)

        labels = [t['name'] for t in treatment_types]
        sizes = [t['count'] for t in treatment_types]
        clrs = COLORS[:len(labels)]

        wedges, _ = ax.pie(
            sizes,
            colors=clrs,
            startangle=90,
            wedgeprops=dict(width=0.48, edgecolor='white', linewidth=2.5)
        )
        ax.axis('equal')

        # Center text: total count
        total = sum(sizes)
        ax.text(0, 0.10, str(total), ha='center', va='center',
                fontsize=16, fontweight='bold', color=TEXT)
        ax.text(0, -0.24, 'Total', ha='center', va='center',
                fontsize=9, color=SUBTEXT)

        # Legend panel on right
        ax2 = fig.add_axes([0.55, 0.05, 0.44, 0.9])
        ax2.set_facecolor(BG)
        ax2.axis('off')

        for i, (lbl, sz, clr) in enumerate(zip(labels, sizes, clrs)):
            pct = sz / total * 100
            y = 0.88 - i * 0.18
            ax2.add_patch(matplotlib.patches.FancyBboxPatch(
                (0, y - 0.06), 0.08, 0.1,
                boxstyle="round,pad=0.01", facecolor=clr, transform=ax2.transAxes
            ))
            ax2.text(0.13, y, lbl, transform=ax2.transAxes,
                     fontsize=9, color=TEXT, va='center', fontweight='500')
            ax2.text(0.13, y - 0.085, f'{sz} ({pct:.0f}%)',
                     transform=ax2.transAxes, fontsize=8, color=SUBTEXT, va='center')

        self.chart_treatment.canvas.draw()

    # ── Payment methods donut ─────────────────────────────────────────────────

    def _draw_payment_methods(self, data):
        fig = self.chart_methods.figure
        fig.clear()
        fig.patch.set_facecolor(BG)

        methods = data['payments']['payment_methods']
        if not methods:
            ax = fig.add_subplot(111)
            self._empty(ax, "No payment data")
            fig.tight_layout(pad=1.2)
            self.chart_methods.canvas.draw()
            return

        ax = fig.add_axes([0.0, 0.05, 0.55, 0.9])
        ax.set_facecolor(BG)

        labels = [m['method'].capitalize() for m in methods]
        sizes = [m['total'] for m in methods]
        clrs = COLORS[:len(labels)]

        wedges, _ = ax.pie(
            sizes, colors=clrs, startangle=90,
            wedgeprops=dict(width=0.48, edgecolor='white', linewidth=2.5)
        )
        ax.axis('equal')

        total = sum(sizes)
        # Whole rupees and a smaller font so the amount fits inside the donut hole
        ax.text(0, 0.10, f"Rs.{total:,.0f}", ha='center', va='center',
                fontsize=9, fontweight='bold', color=TEXT)
        ax.text(0, -0.24, 'Total', ha='center', va='center',
                fontsize=8, color=SUBTEXT)

        ax2 = fig.add_axes([0.55, 0.05, 0.44, 0.9])
        ax2.set_facecolor(BG)
        ax2.axis('off')

        for i, (lbl, sz, clr) in enumerate(zip(labels, sizes, clrs)):
            pct = sz / total * 100
            y = 0.88 - i * 0.18
            ax2.add_patch(matplotlib.patches.FancyBboxPatch(
                (0, y - 0.06), 0.08, 0.1,
                boxstyle="round,pad=0.01", facecolor=clr, transform=ax2.transAxes
            ))
            ax2.text(0.13, y, lbl, transform=ax2.transAxes,
                     fontsize=9, color=TEXT, va='center', fontweight='500')
            ax2.text(0.13, y - 0.085, f'{format_currency(sz)} ({pct:.0f}%)',
                     transform=ax2.transAxes, fontsize=8, color=SUBTEXT, va='center')

        self.chart_methods.canvas.draw()

    # ── Medicines bar chart ───────────────────────────────────────────────────

    def _draw_medicines(self, data):
        fig = self.chart_medicines.figure
        fig.clear()
        ax = fig.add_subplot(111)
        ax.set_facecolor(BG)
        fig.patch.set_facecolor(BG)

        stats = data['prescriptions']['medicine_stats']
        if not stats:
            self._empty(ax, "No prescription data available")
            fig.tight_layout(pad=1.5)
            self.chart_medicines.canvas.draw()
            return

        top = sorted(stats, key=lambda x: x['count'], reverse=True)[:10]
        medicines = [m['medicine'] for m in reversed(top)]
        counts = [m['count'] for m in reversed(top)]

        bars = ax.barh(medicines, counts, color='#1F8A9E', height=0.55,
                       edgecolor='none')

        # Gradient effect: darker for higher bars
        for i, bar in enumerate(bars):
            alpha = 0.5 + 0.5 * (i / max(len(bars) - 1, 1))
            bar.set_alpha(alpha)

        # Value labels inside bars
        for bar, count in zip(bars, counts):
            w = bar.get_width()
            ax.text(w + 0.05, bar.get_y() + bar.get_height() / 2,
                    str(int(w)), va='center', ha='left',
                    fontsize=9, color=TEXT, fontweight='600')

        ax.set_xlabel('Prescriptions', color=SUBTEXT, fontsize=10)
        ax.tick_params(colors=SUBTEXT, labelsize=9)
        ax.spines['left'].set_color('#DDE5E8')
        ax.spines['bottom'].set_color('#DDE5E8')
        ax.set_xlim(0, max(counts) * 1.15)

        fig.tight_layout(pad=1.5)
        self.chart_medicines.canvas.draw()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _empty(self, ax, msg):
        ax.text(0.5, 0.5, msg, ha='center', va='center',
                transform=ax.transAxes, fontsize=12, color=SUBTEXT)
        ax.axis('off')
