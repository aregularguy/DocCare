"""Analytics dashboard — clean, well-sized charts with proper styling."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QGridLayout, QPushButton
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
COLORS = ['#007AFF', '#34C759', '#FF9500', '#5856D6', '#FF3B30', '#00C7BE', '#FF2D55']
BG = '#FFFFFF'
TEXT = '#1D1D1F'
SUBTEXT = '#86868B'

METRIC_ACCENTS = ['#007AFF', '#34C759', '#FF9500', '#5856D6']
METRIC_BG = ['#E5F0FF', '#E8F8EC', '#FFF3E0', '#F0EFFF']
METRIC_ICONS = ['P', 'N', 'Rs', 'T']   # text badges — emoji render as boxes on many systems


# ── Metric card ──────────────────────────────────────────────────────────────

class MetricCard(QFrame):
    def __init__(self, icon, title, value, accent, bg):
        super().__init__()
        self.setObjectName("metric_card")
        self.setStyleSheet(
            f"QFrame#metric_card {{"
            f"  background:{bg}; border-radius:12px;"
            f"  border-left:4px solid {accent};"
            f"}}"
        )
        self.setMinimumHeight(110)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(
            f"font-size:11px; font-weight:bold; color:#fff;"
            f" background:{accent}; border-radius:10px;"
            f" padding:2px 7px;"
        )
        icon_lbl.setMaximumWidth(50)
        top.addWidget(icon_lbl)
        top.addStretch()
        layout.addLayout(top)

        self.value_lbl = QLabel(value)
        # Use setFont for reliable cross-platform rendering; QSS only sets color
        self.value_lbl.setFont(QFont("Ubuntu", 18, QFont.Weight.Bold))
        self.value_lbl.setStyleSheet(f"color:{accent}; background:transparent;")
        self.value_lbl.setWordWrap(False)
        layout.addWidget(self.value_lbl)

        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Ubuntu", 11))
        title_lbl.setStyleSheet(f"color:{SUBTEXT}; background:transparent;")
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
            "QFrame#card { background:#FFFFFF; border:1px solid #E5E5EA;"
            " border-radius:12px; }"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Ubuntu", 13, QFont.Weight.DemiBold))
        title_lbl.setStyleSheet("color:#1D1D1F; background:transparent;")
        layout.addWidget(title_lbl)

        self.figure = Figure(figsize=figsize, dpi=96, facecolor=BG)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setStyleSheet("background:transparent;")
        # Lock the canvas to its natural pixel height so charts don't get
        # squished — the parent QScrollArea will scroll instead.
        canvas_h = int(figsize[1] * 96)  # height in pixels at 96 dpi
        self.canvas.setMinimumHeight(canvas_h)
        self.setMinimumHeight(canvas_h + 60)  # +60 for title + padding
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
            "QFrame { background:#F2F2F7; border-radius:8px; padding:2px; }"
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
            return ("QPushButton { background:#FFFFFF; color:#007AFF; font-weight:600;"
                    " border-radius:6px; padding:5px 14px; font-size:12px; border:none; }")
        return ("QPushButton { background:transparent; color:#86868B; font-weight:400;"
                " border-radius:6px; padding:5px 14px; font-size:12px; border:none; }"
                "QPushButton:hover { color:#1D1D1F; }")

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
        title.setFont(QFont("Ubuntu", 22, QFont.Weight.Bold))
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
        self.m_payments = MetricCard(METRIC_ICONS[2], "Total Collected", "Rs.0",
                                     METRIC_ACCENTS[2], METRIC_BG[2])
        self.m_treatments = MetricCard(METRIC_ICONS[3], "Treatments", "0",
                                       METRIC_ACCENTS[3], METRIC_BG[3])
        metrics_row.addWidget(self.m_patients, 0, 0)
        metrics_row.addWidget(self.m_new, 0, 1)
        metrics_row.addWidget(self.m_payments, 0, 2)
        metrics_row.addWidget(self.m_treatments, 0, 3)
        main.addLayout(metrics_row)

        # ── Payment trends (full width) ──
        self.chart_trends = ChartCard("Payment Trends", figsize=(12, 3.8))
        main.addWidget(self.chart_trends)

        # ── Two donut charts side by side ──
        donuts_row = QHBoxLayout()
        donuts_row.setSpacing(16)
        self.chart_treatment = ChartCard("Treatment Distribution", figsize=(5, 3.8))
        self.chart_methods = ChartCard("Payment Methods", figsize=(5, 3.8))
        donuts_row.addWidget(self.chart_treatment)
        donuts_row.addWidget(self.chart_methods)
        main.addLayout(donuts_row)

        # ── Medicines bar chart (full width) ──
        self.chart_medicines = ChartCard("Top Prescribed Medicines", figsize=(12, 3.5))
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

            ax.plot(dates, amounts, color='#007AFF', linewidth=2.5,
                    marker='o', markersize=5, markerfacecolor='white',
                    markeredgewidth=2, markeredgecolor='#007AFF', zorder=3)
            ax.fill_between(dates, amounts, alpha=0.12, color='#007AFF')

            # Format x-axis dates nicely
            import matplotlib.dates as mdates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
            fig.autofmt_xdate(rotation=30, ha='right')

            ax.set_ylabel('')
            ax.yaxis.set_major_formatter(
                matplotlib.ticker.FuncFormatter(lambda x, _: f'{int(x):,}')
            )
            # Ensure y-axis has sensible tick spacing (avoid overlapping 0 and max)
            ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=5, integer=True))
            ax.set_ylim(bottom=0)
            # "Rs." unit badge at top-left corner of plot area
            ax.annotate('Rs.', xy=(0, 1), xycoords='axes fraction',
                        fontsize=8, color=SUBTEXT, ha='left', va='bottom',
                        xytext=(2, 4), textcoords='offset points')
            ax.tick_params(colors=SUBTEXT, labelsize=9)
            ax.spines['left'].set_color('#E5E5EA')
            ax.spines['bottom'].set_color('#E5E5EA')
        else:
            self._empty(ax, "No payment data for this period")

        fig.tight_layout(pad=1.2)
        fig.subplots_adjust(left=0.09, right=0.97, top=0.93, bottom=0.20)
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

        # Limit to top 5; group rest as "Other"
        sorted_types = sorted(treatment_types, key=lambda t: t['count'], reverse=True)
        if len(sorted_types) > 5:
            top5 = sorted_types[:5]
            other_count = sum(t['count'] for t in sorted_types[5:])
            top5.append({'name': 'Other', 'count': other_count})
            sorted_types = top5

        labels = [t['name'] for t in sorted_types]
        sizes = [t['count'] for t in sorted_types]
        clrs = COLORS[:len(labels)]
        total = sum(sizes)

        # Donut on left
        ax = fig.add_axes([0.0, 0.05, 0.50, 0.9])
        ax.set_facecolor(BG)

        wedges, _ = ax.pie(
            sizes,
            colors=clrs,
            startangle=90,
            wedgeprops=dict(width=0.48, edgecolor='white', linewidth=2.5)
        )
        ax.axis('equal')

        ax.text(0, 0, str(total), ha='center', va='center',
                fontsize=18, fontweight='bold', color=TEXT)
        ax.text(0, -0.22, 'Total', ha='center', va='center',
                fontsize=9, color=SUBTEXT)

        # Legend on right — single line per entry: swatch + name + count
        ax2 = fig.add_axes([0.52, 0.05, 0.46, 0.9])
        ax2.set_facecolor(BG)
        ax2.axis('off')

        n = len(labels)
        row_h = 0.85 / max(n, 1)
        row_h = min(row_h, 0.16)
        for i, (lbl, sz, clr) in enumerate(zip(labels, sizes, clrs)):
            pct = sz / total * 100
            y = 0.90 - i * row_h
            ax2.add_patch(matplotlib.patches.FancyBboxPatch(
                (0.01, y - 0.03), 0.08, 0.06,
                boxstyle="round,pad=0.01", facecolor=clr, transform=ax2.transAxes
            ))
            ax2.text(0.14, y, f'{lbl}  ({sz}, {pct:.0f}%)', transform=ax2.transAxes,
                     fontsize=7.5, color=TEXT, va='center', fontweight='500',
                     clip_on=False)

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

        ax = fig.add_axes([0.0, 0.05, 0.50, 0.9])
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
        ax.text(0, 0, format_currency(total), ha='center', va='center',
                fontsize=10, fontweight='bold', color=TEXT)

        # Legend on right — single line per entry
        ax2 = fig.add_axes([0.52, 0.05, 0.46, 0.9])
        ax2.set_facecolor(BG)
        ax2.axis('off')

        n = len(labels)
        row_h = 0.85 / max(n, 1)
        row_h = min(row_h, 0.16)
        for i, (lbl, sz, clr) in enumerate(zip(labels, sizes, clrs)):
            pct = sz / total * 100
            y = 0.90 - i * row_h
            ax2.add_patch(matplotlib.patches.FancyBboxPatch(
                (0.01, y - 0.03), 0.08, 0.06,
                boxstyle="round,pad=0.01", facecolor=clr, transform=ax2.transAxes
            ))
            ax2.text(0.14, y, f'{lbl}  {format_currency(sz)}  ({pct:.0f}%)',
                     transform=ax2.transAxes, fontsize=7.5, color=TEXT,
                     va='center', fontweight='500', clip_on=False)

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
        medicines = [m['medicine'] for m in top]
        counts = [m['count'] for m in top]

        # Truncate long names for x-axis readability
        short_names = [m[:18] + '…' if len(m) > 18 else m for m in medicines]

        x_pos = range(len(short_names))
        bars = ax.bar(x_pos, counts, color='#007AFF', width=0.55,
                      edgecolor='none')

        # Gradient effect: darker for taller bars
        max_count = max(counts)
        for bar, count in zip(bars, counts):
            alpha = 0.45 + 0.55 * (count / max(max_count, 1))
            bar.set_alpha(alpha)

        # Value labels above bars
        for bar, count in zip(bars, counts):
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + max_count * 0.02,
                    str(int(count)), ha='center', va='bottom',
                    fontsize=9, color=TEXT, fontweight='600')

        ax.set_xticks(x_pos)
        ax.set_xticklabels(short_names, rotation=40, ha='right', fontsize=8)
        ax.set_ylabel('Prescriptions', color=SUBTEXT, fontsize=10)
        ax.tick_params(colors=SUBTEXT, labelsize=9)
        ax.spines['left'].set_color('#E5E5EA')
        ax.spines['bottom'].set_color('#E5E5EA')
        ax.set_ylim(0, max_count * 1.25)

        fig.tight_layout(pad=1.0)
        fig.subplots_adjust(left=0.08, right=0.97, top=0.95, bottom=0.30)
        self.chart_medicines.canvas.draw()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _empty(self, ax, msg):
        ax.text(0.5, 0.5, msg, ha='center', va='center',
                transform=ax.transAxes, fontsize=12, color=SUBTEXT)
        ax.axis('off')
