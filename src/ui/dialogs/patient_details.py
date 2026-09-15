"""Patient details widget - embedded in main window (SimplePractice style)."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QTabWidget,
    QDoubleSpinBox, QComboBox, QDateEdit, QSpinBox,
    QMessageBox, QTextEdit, QDialog, QLineEdit,
    QSizePolicy, QCompleter
)
from PyQt6.QtCore import Qt, QDate, QStringListModel
from PyQt6.QtGui import QFont, QTextDocument, QPageSize
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from ...models.patient import Patient
from ...services.treatment_service import TreatmentService
from ...services.payment_service import PaymentService
from ...services.prescription_service import PrescriptionService
from ...services.settings_service import SettingsService
from ...utils.formatters import format_currency, format_date
from ..widgets.dental_chart_widget import DentalChartWidget
from datetime import date as date_type
import os


class ClickableCard(QFrame):
    """A QFrame that triggers a callback when clicked."""

    def __init__(self, on_click=None, parent=None):
        super().__init__(parent)
        self._on_click = on_click
        if on_click:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        if self._on_click:
            try:
                self._on_click()
            except Exception:
                pass
        super().mousePressEvent(event)


class PatientDetailsWidget(QWidget):
    """Patient details embedded as a full page in the main window stack."""

    def __init__(self, patient: Patient, parent_widget=None):
        super().__init__()
        self.patient = patient
        self.parent_widget = parent_widget
        self.treatment_service = TreatmentService()
        self.payment_service = PaymentService()
        self.prescription_service = PrescriptionService()
        self._refreshing_overview = False  # guard against recursive tab-change signals
        self.treatments = self.treatment_service.get_patient_treatments(patient.id)
        self.total_charged = sum(t.total_cost for t in self.treatments)
        self.total_paid = sum(t.amount_paid for t in self.treatments)
        self.total_due = self.total_charged - self.total_paid
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_header())

        body_widget = QWidget()
        body = QHBoxLayout(body_widget)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # Build combo first — treatment cards reference it
        self.treatment_combo = self._build_treatment_combo()

        self._tabs = QTabWidget()
        self._tabs.setStyleSheet(
            "QTabWidget::pane { border: none; }"
            "QTabBar::tab { padding: 12px 24px; font-size: 13px; }"
            "QTabBar::tab:selected { color: #1F4E5A; font-weight: 700;"
            " border-bottom: 3px solid #3AA9BA; }"
        )
        self._overview_tab_index = 0
        self._tabs.addTab(self._build_overview_tab(), "Overview")
        self._tabs.addTab(self._build_billing_tab(), "Billing")
        self._tabs.addTab(self._build_prescription_tab(), "📋 Prescription")

        # Dental Chart tab
        self._dental_chart_widget = DentalChartWidget(self.patient.id)
        self._dental_chart_tab_index = 3
        self._tabs.addTab(self._dental_chart_widget, "🦷 Dental Chart")

        self._tabs.currentChanged.connect(self._on_tab_changed)
        body.addWidget(self._tabs, stretch=3)
        tabs = self._tabs  # keep local alias for billing panel below

        body.addWidget(self._build_billing_panel(), stretch=0)

        layout.addWidget(body_widget)

    # ── Header ──────────────────────────────────────────────────────────────

    def _build_header(self):
        header = QFrame()
        header.setStyleSheet("background:#fff; border-bottom:1px solid #DDE5E8;")
        hl = QVBoxLayout(header)
        hl.setContentsMargins(32, 16, 32, 16)
        hl.setSpacing(10)

        top = QHBoxLayout()

        back_btn = QPushButton("← Back to Patients")
        back_btn.setObjectName("secondary_button")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self._on_back)
        top.addWidget(back_btn)

        top.addStretch()

        name_label = QLabel(f"👤  {self.patient.name}")
        name_label.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        name_label.setStyleSheet("color:#1E2B32;")
        top.addWidget(name_label)

        top.addStretch()

        hl.addLayout(top)

        # Meta pills row
        meta_row = QHBoxLayout()
        meta_row.setSpacing(0)

        def make_pill(text, text_color="#4A4A4F", bg="#EEF3F4"):
            lbl = QLabel(text)
            lbl.setStyleSheet(
                f"color:{text_color}; background:{bg}; padding:4px 10px;"
                f"border-radius:12px; font-size:12px; font-weight:500;"
            )
            return lbl

        def make_sep():
            s = QLabel("•")
            s.setStyleSheet("color:#A9B6BC; padding:0 8px; font-size:13px; background:transparent;")
            return s

        meta_row.addWidget(make_pill(f"Age {self.patient.age}"))
        meta_row.addWidget(make_sep())
        meta_row.addWidget(make_pill(self.patient.city))
        meta_row.addWidget(make_sep())
        meta_row.addWidget(make_pill(f"ID #{self.patient.id}"))
        meta_row.addWidget(make_sep())
        meta_row.addWidget(make_pill(f"Ph: {self.patient.mobile_number}"))
        meta_row.addWidget(make_sep())
        meta_row.addWidget(make_pill(f"Charged: {format_currency(self.total_charged)}", "#1E2B32", "#EEF3F4"))
        meta_row.addWidget(make_sep())
        meta_row.addWidget(make_pill(f"Paid: {format_currency(self.total_paid)}", "#2E9E6B", "#E6F5EE"))
        meta_row.addWidget(make_sep())
        due_color = "#D0534F" if self.total_due > 0 else "#2E9E6B"
        due_bg = "#FBEBEA" if self.total_due > 0 else "#E6F5EE"
        meta_row.addWidget(make_pill(f"Due: {format_currency(self.total_due)}", due_color, due_bg))
        meta_row.addStretch()

        hl.addLayout(meta_row)

        return header

    # ── Treatment combo (shared between overview cards and billing panel) ──

    def _build_treatment_combo(self):
        combo = QComboBox()
        for t in self.treatments:
            label = t.treatment_type_name or "Treatment"
            if t.pending_amount > 0:
                label += f"  (Due: {format_currency(t.pending_amount)})"
            else:
                label += "  ✅ Fully Paid"
            combo.addItem(label, t.id)
        return combo

    # ── Tab switching ────────────────────────────────────────────────────────

    def _on_tab_changed(self, index: int):
        if index == self._overview_tab_index:
            self._refresh_overview()
        elif index == self._dental_chart_tab_index:
            # Refresh chart in case conditions were changed externally
            try:
                self._dental_chart_widget.refresh()
            except Exception:
                pass

    def _refresh_overview(self):
        """Rebuild the overview tab content in-place.

        Guard against re-entrant calls: removeTab() fires currentChanged which
        would recurse back here and crash the application.
        """
        if self._refreshing_overview:
            return
        self._refreshing_overview = True
        try:
            # Re-fetch treatments so new prescriptions/payments appear
            self.treatments = self.treatment_service.get_patient_treatments(self.patient.id)
            self.total_charged = sum(t.total_cost for t in self.treatments)
            self.total_paid = sum(t.amount_paid for t in self.treatments)
            self.total_due = self.total_charged - self.total_paid

            old_widget = self._tabs.widget(self._overview_tab_index)
            new_widget = self._build_overview_tab()
            # Block signals while manipulating tabs to avoid currentChanged firing
            self._tabs.blockSignals(True)
            self._tabs.removeTab(self._overview_tab_index)
            self._tabs.insertTab(self._overview_tab_index, new_widget, "Overview")
            self._tabs.setCurrentIndex(self._overview_tab_index)
            self._tabs.blockSignals(False)
            if old_widget:
                old_widget.deleteLater()
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error refreshing overview tab: {e}")
        finally:
            self._refreshing_overview = False

    # ── Overview tab ────────────────────────────────────────────────────────

    def _build_overview_tab(self):
        widget = QWidget()
        outer = QVBoxLayout(widget)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(32, 24, 24, 24)
        layout.setSpacing(16)

        if not self.treatments:
            empty = QLabel("No treatments recorded yet.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color:#5B6B73; padding:60px;")
            layout.addWidget(empty)
        else:
            treatments_title = QLabel("🦷 Treatments")
            treatments_title.setFont(QFont("Inter", 15, QFont.Weight.DemiBold))
            treatments_title.setStyleSheet("color:#1E2B32; margin-bottom:4px;")
            layout.addWidget(treatments_title)

            for t in self.treatments:
                layout.addWidget(self._build_treatment_card(t))

            # Prescriptions section — grouped by session
            prescription_service = PrescriptionService()
            all_prescriptions = []
            for t in self.treatments:
                all_prescriptions.extend(
                    prescription_service.get_treatment_prescriptions(t.id)
                )

            rx_title = QLabel("💊 Prescriptions")
            rx_title.setFont(QFont("Inter", 15, QFont.Weight.DemiBold))
            rx_title.setStyleSheet("color:#1E2B32; margin-top:8px; margin-bottom:4px;")
            layout.addWidget(rx_title)

            if not all_prescriptions:
                no_rx = QLabel("No prescriptions recorded")
                no_rx.setStyleSheet("color:#5B6B73; font-size:13px; padding:6px 0;")
                layout.addWidget(no_rx)
            else:
                # Group by session_id (preserving insertion order = newest first via DB ORDER BY DESC)
                from collections import OrderedDict
                sessions: OrderedDict = OrderedDict()
                for rx in all_prescriptions:
                    # Prescriptions without a session_id each form their own group (old data)
                    key = rx.session_id if rx.session_id else f"__solo_{rx.id}"
                    sessions.setdefault(key, []).append(rx)

                for session_num, (key, meds) in enumerate(sessions.items(), 1):
                    layout.addWidget(self._build_prescription_session_card(session_num, meds))

        layout.addStretch()
        scroll.setWidget(inner)
        outer.addWidget(scroll)
        return widget

    def _build_prescription_session_card(self, session_num: int, meds: list):
        """A grouped card showing all medicines from one prescription session."""
        card = QFrame()
        card.setObjectName("rx_session_card")
        card.setStyleSheet(
            "QFrame#rx_session_card {"
            "  background: #F7FAFB;"
            "  border: 1px solid #B9DCE4;"
            "  border-left: 4px solid #1F8A9E;"
            "  border-radius: 8px;"
            "  margin-bottom: 8px;"
            "}"
        )
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(14, 10, 14, 10)
        vbox.setSpacing(4)

        # Header row: "Prescription #N  ·  DD Mon YYYY"
        header = QHBoxLayout()
        header.setSpacing(8)

        num_lbl = QLabel(f"Prescription #{session_num}")
        num_lbl.setFont(QFont("Ubuntu", 12, QFont.Weight.Bold))
        num_lbl.setStyleSheet("color:#16707F;")
        header.addWidget(num_lbl)

        if meds[0].prescribed_date:
            date_str = meds[0].prescribed_date.strftime("%d %b %Y")
            date_lbl = QLabel(f"  📅 {date_str}")
            date_lbl.setStyleSheet("color:#5B6B73; font-size:12px;")
            header.addWidget(date_lbl)

        header.addStretch()
        med_count = QLabel(f"{len(meds)} medicine{'s' if len(meds) != 1 else ''}")
        med_count.setStyleSheet(
            "color:#16707F; background:#CDEAF0; border-radius:8px;"
            " padding:2px 8px; font-size:11px; font-weight:600;"
        )
        header.addWidget(med_count)
        vbox.addLayout(header)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet("color:#B9DCE4; margin: 2px 0;")
        vbox.addWidget(div)

        # One row per medicine
        for rx in meds:
            med_row = QHBoxLayout()
            med_row.setSpacing(10)

            bullet = QLabel("•")
            bullet.setFixedWidth(12)
            bullet.setStyleSheet("color:#1F8A9E; font-size:14px;")
            med_row.addWidget(bullet)

            name_lbl = QLabel(rx.medicine_name)
            name_lbl.setFont(QFont("Ubuntu", 12, QFont.Weight.Medium))
            name_lbl.setStyleSheet("color:#1E2B32;")
            med_row.addWidget(name_lbl)

            detail_parts = [p for p in [rx.dosage, rx.frequency, rx.duration] if p]
            if detail_parts:
                detail_lbl = QLabel("  ·  ".join(detail_parts))
                detail_lbl.setStyleSheet("color:#5B6B73; font-size:12px;")
                med_row.addWidget(detail_lbl)

            med_row.addStretch()
            vbox.addLayout(med_row)

        return card

    def _build_treatment_card(self, treatment):
        """Clickable treatment card — click selects it in the billing panel combo."""

        def on_click():
            for i in range(self.treatment_combo.count()):
                if self.treatment_combo.itemData(i) == treatment.id:
                    self.treatment_combo.setCurrentIndex(i)
                    break

        card = ClickableCard(on_click if treatment.pending_amount > 0 else None)
        card.setObjectName("card")
        card.setStyleSheet(
            "QFrame#card { border-left: 4px solid #1F8A9E; margin-bottom: 8px; }"
            "QFrame#card:hover { background: #EEF7F9; }"
        )

        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        # Row 1: treatment name + status badge
        row1 = QHBoxLayout()
        type_label = QLabel(f"🦷  {treatment.treatment_type_name or 'Treatment'}")
        type_label.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        row1.addWidget(type_label)
        row1.addStretch()

        status_colors = {
            "planned": "#C98A2E",
            "in_progress": "#1F8A9E",
            "completed": "#2E9E6B"
        }
        color = status_colors.get(treatment.status, "#5B6B73")
        badge = QLabel(treatment.status.replace("_", " ").upper())
        badge.setStyleSheet(
            f"color:white; background:{color}; padding:3px 10px;"
            f"border-radius:10px; font-size:11px; font-weight:600;"
        )
        row1.addWidget(badge)
        layout.addLayout(row1)

        # Row 2: date
        date_str = treatment.start_date.strftime("%d %b %Y") if treatment.start_date else "N/A"
        date_lbl = QLabel(f"📅  {date_str}")
        date_lbl.setStyleSheet("color:#5B6B73; font-size:12px; margin-bottom:6px;")
        layout.addWidget(date_lbl)

        # Row 3: colored metric boxes
        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(10)

        metrics_row.addWidget(self._metric_box("Total Cost", format_currency(treatment.total_cost), "#6E72B8", "#EEEFF8"))
        metrics_row.addWidget(self._metric_box("Paid", format_currency(treatment.amount_paid), "#2E9E6B", "#E6F5EE"))
        metrics_row.addWidget(self._metric_box(
            "Pending",
            format_currency(treatment.pending_amount),
            "#D0534F" if treatment.pending_amount > 0 else "#2E9E6B",
            "#FBEBEA" if treatment.pending_amount > 0 else "#E6F5EE"
        ))
        metrics_row.addStretch()
        layout.addLayout(metrics_row)

        if treatment.notes:
            notes_lbl = QLabel(f"📝  {treatment.notes}")
            notes_lbl.setStyleSheet("color:#5B6B73; font-size:12px; margin-top:4px;")
            notes_lbl.setWordWrap(True)
            layout.addWidget(notes_lbl)

        # Click hint only when there's a pending amount
        if treatment.pending_amount > 0:
            hint = QLabel("Click to select for payment →")
            hint.setStyleSheet("color:#1F8A9E; font-size:11px;")
            hint.setAlignment(Qt.AlignmentFlag.AlignRight)
            layout.addWidget(hint)

        return card

    def _metric_box(self, label, value, text_color, bg_color):
        """A small colored metric pill: label on top, bold value below."""
        box = QFrame()
        box.setStyleSheet(
            f"background:{bg_color}; border-radius:8px; padding:2px;"
        )
        box.setFixedWidth(120)
        bl = QVBoxLayout(box)
        bl.setContentsMargins(10, 8, 10, 8)
        bl.setSpacing(2)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"color:{text_color}; font-size:10px; font-weight:500;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bl.addWidget(lbl)

        val = QLabel(value)
        val.setStyleSheet(f"color:{text_color}; font-size:14px; font-weight:700;")
        val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bl.addWidget(val)

        return box

    # ── Billing tab ─────────────────────────────────────────────────────────

    def _build_billing_tab(self):
        """Billing tab — click any row to expand/collapse its payment history."""
        outer = QWidget()
        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(32, 24, 24, 24)
        layout.setSpacing(0)

        if not self.treatments:
            empty = QLabel("No billing records.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color:#5B6B73; padding:60px;")
            layout.addWidget(empty)
        else:
            for t in self.treatments:
                try:
                    layout.addWidget(self._build_billing_row(t))
                except Exception:
                    pass

        layout.addStretch()
        scroll.setWidget(inner)
        outer_layout.addWidget(scroll)
        return outer

    def _build_billing_row(self, treatment):
        """One treatment row + collapsible payment history panel."""
        container = QFrame()
        container.setStyleSheet("border-bottom:1px solid #EEF3F4;")
        cl = QVBoxLayout(container)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)

        # ── Payment history panel (hidden by default) ──
        history_panel = QFrame()
        history_panel.setStyleSheet(
            "background:#F4F7F8; border-radius:6px; margin:0 4px 8px 4px;"
        )
        hl = QVBoxLayout(history_panel)
        hl.setContentsMargins(16, 10, 16, 10)
        hl.setSpacing(6)
        history_panel.setVisible(False)

        payments = self.payment_service.get_treatment_payments(treatment.id)
        if payments:
            header_row = QHBoxLayout()
            for col in ["Date", "Method", "Amount"]:
                lbl = QLabel(col)
                lbl.setStyleSheet("color:#5B6B73; font-size:11px; font-weight:600;")
                header_row.addWidget(lbl)
                if col != "Amount":
                    header_row.addStretch()
            hl.addLayout(header_row)

            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet("color:#DDE5E8;")
            hl.addWidget(sep)

            for p in payments:
                p_row = QHBoxLayout()
                try:
                    from datetime import date as _date, datetime as _dt
                    pd = p.payment_date
                    if isinstance(pd, str):
                        pd = _dt.fromisoformat(pd).date()
                    date_str = pd.strftime("%d %b %Y") if pd else "N/A"
                except Exception:
                    date_str = str(p.payment_date) if p.payment_date else "N/A"
                date_lbl = QLabel(f"📅 {date_str}")
                date_lbl.setStyleSheet("font-size:13px;")
                p_row.addWidget(date_lbl)
                p_row.addStretch()

                method_lbl = QLabel((p.payment_method or "cash").capitalize())
                method_lbl.setStyleSheet("color:#5B6B73; font-size:12px;")
                p_row.addWidget(method_lbl)
                p_row.addStretch()

                amount_lbl = QLabel(format_currency(p.amount))
                amount_lbl.setStyleSheet("color:#2E9E6B; font-weight:600; font-size:13px;")
                p_row.addWidget(amount_lbl)

                row_w = QWidget()
                row_w.setLayout(p_row)
                hl.addWidget(row_w)
        else:
            no_pay = QLabel("No payments recorded yet.")
            no_pay.setStyleSheet("color:#5B6B73; font-size:12px;")
            hl.addWidget(no_pay)

        # ── Arrow label (toggled on click) ──
        arrow = QLabel("v")
        arrow.setStyleSheet("color:#5B6B73; margin-left:8px; font-size:11px; font-weight:700;")

        def toggle(_hp=history_panel, _ar=arrow):
            try:
                visible = not _hp.isVisible()
                _hp.setVisible(visible)
                _ar.setText("^" if visible else "v")
            except Exception:
                pass

        # ── Main clickable row ──
        row_card = ClickableCard(toggle)
        row_card.setStyleSheet("QFrame:hover { background:#F4F7F8; }")
        rl = QHBoxLayout(row_card)
        rl.setContentsMargins(4, 12, 4, 12)

        name_lbl = QLabel(f"🦷  {treatment.treatment_type_name or 'Treatment'}")
        name_lbl.setStyleSheet("font-size:13px; font-weight:500;")
        rl.addWidget(name_lbl)
        rl.addStretch()

        charged_lbl = QLabel(format_currency(treatment.total_cost))
        charged_lbl.setStyleSheet("font-size:13px;")
        rl.addWidget(charged_lbl)

        rl.addWidget(QLabel("   Paid: "))
        paid_lbl = QLabel(format_currency(treatment.amount_paid))
        paid_lbl.setStyleSheet("color:#2E9E6B; font-weight:600;")
        rl.addWidget(paid_lbl)

        rl.addWidget(QLabel("   Due: "))
        due_lbl = QLabel(format_currency(treatment.pending_amount))
        due_lbl.setStyleSheet("color:#D0534F; font-weight:600;")
        rl.addWidget(due_lbl)

        rl.addWidget(arrow)

        cl.addWidget(row_card)
        cl.addWidget(history_panel)
        return container

    # ── Right billing panel ──────────────────────────────────────────────────

    def _build_billing_panel(self):
        panel = QFrame()
        panel.setStyleSheet("background:#F4F7F8; border-left:1px solid #DDE5E8;")
        panel.setFixedWidth(260)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 24, 20, 24)
        layout.setSpacing(12)

        title = QLabel("Client Billing")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        layout.addWidget(title)

        layout.addWidget(self._billing_row_label("Total Charged", format_currency(self.total_charged), "#1E2B32"))
        layout.addWidget(self._billing_row_label("Total Paid", format_currency(self.total_paid), "#2E9E6B"))
        layout.addWidget(self._billing_row_label("Total Due", format_currency(self.total_due), "#D0534F"))

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color:#DDE5E8;")
        layout.addWidget(sep)

        sel_label = QLabel("Select Treatment:")
        sel_label.setStyleSheet("font-size:12px; color:#5B6B73;")
        layout.addWidget(sel_label)

        layout.addWidget(self.treatment_combo)

        add_btn = QPushButton("➕ Add Payment")
        add_btn.setObjectName("primary_button")
        add_btn.setStyleSheet("color: white; font-weight: bold;")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._show_add_payment)
        layout.addWidget(add_btn)

        layout.addStretch()
        return panel

    def _billing_row_label(self, label, value, color):
        row = QFrame()
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel(label)
        lbl.setStyleSheet("color:#5B6B73; font-size:13px;")
        val = QLabel(value)
        val.setStyleSheet(f"color:{color}; font-weight:600; font-size:13px;")
        rl.addWidget(lbl)
        rl.addStretch()
        rl.addWidget(val)
        return row

    # ── Actions ─────────────────────────────────────────────────────────────

    def _show_add_payment(self):
        treatment_id = self.treatment_combo.currentData()
        if treatment_id is None:
            QMessageBox.warning(self, "No Treatment", "No pending treatments to pay for.")
            return

        dialog = AddPaymentDialog(treatment_id, self.payment_service, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Refresh by re-pushing this widget
            if self.parent_widget:
                self.parent_widget.show_patient_details(self.patient)

    def _on_back(self):
        if self.parent_widget:
            self.parent_widget.show_list_view()

    # ── Prescription Tab ─────────────────────────────────────────────────────

    def _build_prescription_tab(self):
        """Build the TatvaCare-style prescription editor tab."""
        widget = QWidget()
        outer = QVBoxLayout(widget)
        outer.setContentsMargins(24, 20, 24, 20)
        outer.setSpacing(14)

        # ── Top bar ──
        top = QHBoxLayout()
        title = QLabel("📋  Create Prescription")
        title.setStyleSheet("font-size:16px; font-weight:700; color:#1F4E5A;")
        top.addWidget(title)
        top.addStretch()

        # Treatment selector
        top.addWidget(QLabel("For Treatment:"))
        self._rx_treatment_combo = QComboBox()
        self._rx_treatment_combo.setFixedWidth(220)
        for t in self.treatments:
            label = t.treatment_type_name or "Treatment"
            self._rx_treatment_combo.addItem(label, t.id)
        top.addWidget(self._rx_treatment_combo)

        # Date
        top.addWidget(QLabel("  Date:"))
        self._rx_date = QDateEdit()
        self._rx_date.setDate(QDate.currentDate())
        self._rx_date.setCalendarPopup(True)
        self._rx_date.setFixedWidth(120)
        top.addWidget(self._rx_date)
        outer.addLayout(top)

        # ── Column header ──
        header_frame = QFrame()
        header_frame.setStyleSheet(
            "QFrame { background:#1F4E5A; border-radius:8px 8px 0 0; }"
        )
        hh = QHBoxLayout(header_frame)
        hh.setContentsMargins(10, 8, 10, 8)
        hh.setSpacing(0)

        def _hcol(txt, w):
            l = QLabel(txt)
            l.setFixedWidth(w)
            l.setStyleSheet("color:white; font-size:11px; font-weight:700; background:transparent;")
            l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return l

        hh.addWidget(_hcol("#", 30))
        hh.addWidget(_hcol("Medicine Name", 260))
        hh.addWidget(_hcol("Dosage (M-A-E-N)", 240))
        hh.addWidget(_hcol("Timing", 220))
        hh.addWidget(_hcol("Qty", 80))
        hh.addWidget(_hcol("", 40))
        outer.addWidget(header_frame)

        # ── Rows container (scrollable) ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setMinimumHeight(200)

        self._rx_rows_widget = QWidget()
        self._rx_rows_widget.setStyleSheet("background:#F4F7F8;")
        self._rx_rows_layout = QVBoxLayout(self._rx_rows_widget)
        self._rx_rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rx_rows_layout.setSpacing(2)
        self._rx_rows_layout.addStretch()
        scroll.setWidget(self._rx_rows_widget)
        outer.addWidget(scroll)

        self._rx_rows = []  # list of PrescriptionRowWidget
        self._medicine_names = [m.name for m in self.prescription_service.get_all_medicines()]

        # Start with 2 empty rows
        self._add_rx_row()
        self._add_rx_row()

        # ── Bottom bar ──
        bot = QHBoxLayout()
        add_row_btn = QPushButton("➕  Add Medicine Row")
        add_row_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_row_btn.setStyleSheet(
            "QPushButton { background:#E3F3F6; color:#2A6674; border:1px solid #B9DCE4;"
            " border-radius:7px; padding:8px 16px; font-weight:600; }"
            "QPushButton:hover { background:#CDEAF0; }"
        )
        add_row_btn.clicked.connect(self._add_rx_row)
        bot.addWidget(add_row_btn)
        bot.addStretch()

        save_btn = QPushButton("💾  Save Prescription")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(
            "QPushButton { background:#2E9E6B; color:white; border:none;"
            " border-radius:7px; padding:8px 20px; font-weight:700; }"
            "QPushButton:hover { background:#2A9163; }"
        )
        save_btn.clicked.connect(self._save_prescriptions)
        bot.addWidget(save_btn)

        print_btn = QPushButton("🖨️  Print / PDF")
        print_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        print_btn.setStyleSheet(
            "QPushButton { background:#1F4E5A; color:white; border:none;"
            " border-radius:7px; padding:8px 20px; font-weight:700; }"
            "QPushButton:hover { background:#2A6674; }"
        )
        print_btn.clicked.connect(self._print_prescription)
        bot.addWidget(print_btn)
        outer.addLayout(bot)

        return widget

    def _add_rx_row(self):
        row = _PrescriptionRowWidget(
            row_num=len(self._rx_rows) + 1,
            medicine_names=self._medicine_names,
            on_delete=self._delete_rx_row
        )
        self._rx_rows.append(row)
        # Insert before the stretch
        idx = self._rx_rows_layout.count() - 1
        self._rx_rows_layout.insertWidget(idx, row)

    def _delete_rx_row(self, row_widget):
        if row_widget in self._rx_rows:
            self._rx_rows.remove(row_widget)
            self._rx_rows_layout.removeWidget(row_widget)
            row_widget.deleteLater()
            # Renumber
            for i, r in enumerate(self._rx_rows):
                r.set_num(i + 1)

    def _save_prescriptions(self):
        treatment_id = self._rx_treatment_combo.currentData()
        if treatment_id is None:
            QMessageBox.warning(self, "No Treatment", "Please select a treatment first.")
            return

        import uuid
        session_id = str(uuid.uuid4())  # one UUID ties all medicines in this save together
        rx_date = self._rx_date.date().toPyDate()
        saved = 0
        for row in self._rx_rows:
            data = row.get_data()
            if not data["medicine"]:
                continue
            dosage_str = f"{data['M']}-{data['A']}-{data['E']}-{data['N']}"
            ok, _, _ = self.prescription_service.add_prescription(
                treatment_id=treatment_id,
                medicine_name=data["medicine"],
                session_id=session_id,
                dosage=dosage_str,
                frequency=data["timing"],
                duration=f"{data['days']}",
                prescribed_date=rx_date,
                notes=None
            )
            if ok:
                saved += 1

        if saved:
            QMessageBox.information(self, "Saved", f"✅ {saved} medicine(s) saved as one prescription!")
            self._refresh_overview()
        else:
            QMessageBox.warning(self, "Nothing saved", "Please fill at least one medicine row.")

    def _print_prescription(self):
        """Generate HTML prescription and show print/PDF dialog."""
        # ── load clinic/doctor settings ──────────────────────────────
        s = SettingsService().get_all()
        clinic_en   = s.get("clinic_name_english") or "DentNest Dental Clinic"
        clinic_mr   = s.get("clinic_name_marathi", "")
        address     = s.get("clinic_address", "")
        phone       = s.get("clinic_phone", "")
        timing      = s.get("clinic_timing", "")
        doctor_name = s.get("doctor_name") or "Dr. __________"
        degree      = s.get("degree") or "BDS / MDS"
        reg_number  = s.get("reg_number") or "___________"
        logo_path   = s.get("logo_path", "")

        # Build centre sub-lines (only non-empty)
        center_lines = ""
        if clinic_mr:
            center_lines += f"<div class='clinic-sub' style='font-size:12pt; color:#1F4E5A; font-weight:600;'>{clinic_mr}</div>"
        if address:
            center_lines += f"<div class='clinic-sub'>{address}</div>"
        if phone:
            center_lines += f"<div class='clinic-sub'>📞 {phone}</div>"
        if timing:
            center_lines += f"<div class='clinic-sub'>{timing}</div>"

        # Logo cell (right side — only if file exists)
        if logo_path and os.path.exists(logo_path):
            logo_cell = (
                f"<td class='lh-logo'>"
                f"<img src='{logo_path}' width='70' height='70'"
                f" style='border-radius:35px; object-fit:cover;'/>"
                f"</td>"
            )
        else:
            logo_cell = ""

        today = self._rx_date.date()
        date_str = today.toString("dd-MMM-yyyy")

        rows_html = ""
        for i, row in enumerate(self._rx_rows):
            d = row.get_data()
            if not d["medicine"]:
                continue
            timing_mr = "जेवणापूर्वी" if "Before" in d["timing"] else (
                "जेवणासह" if "With" in d["timing"] else "जेवणानंतर"
            )
            dosage_str = f"{d['M']} - {d['A']} - {d['E']} - {d['N']}"
            rows_html += f"""
            <tr>
              <td style='text-align:center;'>{i+1}</td>
              <td style='padding-left:8px;'><span class='med-name'>{d['medicine']}</span></td>
              <td style='text-align:center; font-size:10pt; font-weight:700; letter-spacing:1px;'>{dosage_str}</td>
              <td style='text-align:center;'><span class='timing-mr'>{timing_mr}</span></td>
              <td style='text-align:center; font-weight:700;'>{d['days']}</td>
            </tr>"""

        if not rows_html:
            QMessageBox.warning(self, "Empty", "Please add at least one medicine.")
            return

        html = f"""
        <html><head>
        <meta charset="UTF-8"/>
        <style>
          body {{
            font-family: 'Noto Sans', 'Noto Sans Devanagari', 'DejaVu Sans', Arial, sans-serif;
            margin: 36px 40px;
            font-size: 15pt;
            color: #1a1a1a;
          }}

          /* ── Letterhead ── */
          .letterhead {{
            width: 100%;
            border-collapse: collapse;
            border-bottom: 3px double #1F4E5A;
            padding-bottom: 10px;
            margin-bottom: 14px;
          }}
          .lh-symbol {{
            width: 56px;
            vertical-align: middle;
            text-align: center;
          }}
          .lh-symbol .tooth-icon {{
            display: inline-block;
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background: #1F4E5A;
            color: white;
            font-size: 26pt;
            line-height: 48px;
            text-align: center;
          }}
          .lh-center {{
            text-align: center;
            vertical-align: middle;
            padding: 0 10px;
          }}
          .lh-center .clinic-name {{
            font-size: 18pt;
            font-weight: 900;
            color: #1F4E5A;
            letter-spacing: 0.5px;
          }}
          .lh-center .clinic-sub {{
            font-size: 10pt;
            color: #555;
            margin-top: 2px;
          }}
          .lh-right {{
            width: 200px;
            vertical-align: middle;
            text-align: right;
            padding-right: 4px;
          }}
          .lh-right .doc-name {{
            font-size: 16pt;
            font-weight: 800;
            color: #1F4E5A;
          }}
          .lh-right .doc-degree {{
            font-size: 11pt;
            color: #444;
            margin-top: 2px;
          }}
          .lh-right .doc-reg {{
            font-size: 10pt;
            color: #888;
          }}
          .lh-logo {{
            width: 80px;
            vertical-align: middle;
            text-align: center;
            padding-left: 8px;
          }}

          /* ── Patient strip ── */
          .header-divider {{
            border: none;
            border-top: 2px solid #1F4E5A;
            margin: 10px 0 0 0;
          }}
          .patient-strip {{
            width: 100%;
            border-collapse: collapse;
            background: #E3F3F6;
            margin: 10px 0 14px 0;
            table-layout: fixed;
          }}
          .patient-strip td {{
            padding: 6px 10px;
            border: none;
            width: 25%;
          }}
          .patient-strip .label {{
            font-size: 8pt;
            color: #666;
            display: block;
            white-space: nowrap;
          }}
          .patient-strip .value {{
            font-size: 9pt;
            font-weight: 700;
            color: #1F4E5A;
            display: block;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }}

          /* ── Prescription table ── */
          .rx-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            table-layout: fixed;
          }}
          .rx-table th {{
            background: #1F4E5A;
            color: white;
            padding: 6px 4px;
            font-size: 9pt;
            text-align: center;
            border: 1px solid #1E2B32;
            word-break: keep-all;
            white-space: nowrap;
          }}
          .rx-table td {{
            padding: 6px 5px;
            font-size: 10pt;
            border: 1px solid #CFDADE;
            vertical-align: middle;
          }}
          /* Column widths: fixed layout lets medicine column breathe */
          .col-num      {{ width: 28px; text-align:center; }}
          .col-med      {{ width: 42%; }}
          .col-dosage   {{ width: 16%; text-align:center; }}
          .col-timing   {{ width: 26%; text-align:center; }}
          .col-qty      {{ width: 12%; text-align:center; }}

          .rx-table tr:nth-child(even) td {{
            background: #EEF7F9;
          }}
          .med-name {{ font-weight: 700; font-size: 10pt; word-break: normal; }}
          .timing-mr {{ font-size: 9pt; color: #1F4E5A; font-weight: 600; }}

          /* ── Footer ── */
          .footer-line {{
            border-top: 1px dashed #aaa;
            margin-top: 50px;
            padding-top: 8px;
            text-align: right;
          }}
          .footer-line .sig-line {{
            font-size: 13pt;
            color: #1F4E5A;
            font-weight: 700;
          }}
        </style>
        </head><body>

        <!-- ═══ LETTERHEAD ═══ -->
        <table class="letterhead">
          <tr>
            <td class="lh-symbol">
              <span class="tooth-icon">🦷</span>
            </td>
            <td class="lh-center">
              <div class="clinic-name">{clinic_en}</div>
              {center_lines}
            </td>
            <td class="lh-right">
              <div class="doc-name">{doctor_name}</div>
              <div class="doc-degree">{degree}</div>
              <div class="doc-reg">Reg. No. : {reg_number}</div>
            </td>
            {logo_cell}
          </tr>
        </table>

        <hr class="header-divider"/>

        <!-- ═══ PATIENT DETAILS ═══ -->
        <table class="patient-strip">
          <tr>
            <td>
              <span class="label">Patient</span>
              <span class="value">{self.patient.name}</span>
            </td>
            <td>
              <span class="label">Age</span>
              <span class="value">{self.patient.age} yrs</span>
            </td>
            <td>
              <span class="label">Mobile</span>
              <span class="value">{self.patient.mobile_number}</span>
            </td>
            <td>
              <span class="label">Date</span>
              <span class="value">{date_str}</span>
            </td>
          </tr>
        </table>

        <div style="font-size:11pt; color:#1F4E5A; font-weight:700; margin-bottom:8px; letter-spacing:0.5px;">
          Rx &nbsp; Prescription / औषध यादी
        </div>

        <!-- ═══ PRESCRIPTION TABLE ═══ -->
        <table class="rx-table">
          <colgroup>
            <col class="col-num"/>
            <col class="col-med"/>
            <col class="col-dosage"/>
            <col class="col-timing"/>
            <col class="col-qty"/>
          </colgroup>
          <thead>
            <tr>
              <th>#</th>
              <th style="text-align:left; padding-left:8px;">Medicine / औषध</th>
              <th>Dosage<br/><span style="font-size:9pt; font-weight:400;">(M - A - E - N)</span></th>
              <th>Timing / वेळ</th>
              <th>Quantity</th>
            </tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>

        <!-- ═══ FOOTER / SIGNATURE ═══ -->
        <div class="footer-line">
          <br/>
          <span class="sig-line">_________________________________</span><br/>
          <span class="sig-line">{doctor_name}</span>
        </div>

        </body></html>
        """

        doc = QTextDocument()
        doc.setHtml(html)

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        # Give the document proper page width for layout
        doc.setPageSize(printer.pageRect(QPrinter.Unit.Point).size())

        preview = QPrintPreviewDialog(printer, self)
        preview.setWindowTitle("🖨️  Print / Save Prescription as PDF")
        preview.paintRequested.connect(lambda p: doc.print(p))
        preview.resize(1000, 760)
        preview.exec()


# Keep old name as alias so any other imports don't break
PatientDetailsDialog = PatientDetailsWidget


# ── Add Payment Dialog ───────────────────────────────────────────────────────

class AddPaymentDialog(QDialog):
    """Premium-styled payment entry dialog with auto-close on success."""

    def __init__(self, treatment_id: int, payment_service: PaymentService, parent=None):
        super().__init__(parent)
        self.treatment_id = treatment_id
        self.payment_service = payment_service
        self.setWindowTitle("Add Payment")
        self.setMinimumWidth(480)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.init_ui()

    def init_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Gradient header ──
        header = QFrame()
        header.setStyleSheet(
            "QFrame { background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            " stop:0 #1F4E5A, stop:0.6 #2A6674, stop:1 #3A8C99);"
            " border-radius: 0px; }"
        )
        header.setFixedHeight(64)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(24, 0, 24, 0)

        icon_lbl = QLabel("💳")
        icon_lbl.setStyleSheet("font-size:24px; background:transparent;")
        hl.addWidget(icon_lbl)

        title_lbl = QLabel("  Add Payment")
        title_lbl.setStyleSheet(
            "color:white; font-size:17px; font-weight:700; background:transparent;"
        )
        hl.addWidget(title_lbl)
        hl.addStretch()

        # Due badge
        from ...services.treatment_service import TreatmentService
        try:
            treatment = TreatmentService().get_treatment_by_id(self.treatment_id)
            if treatment and treatment.pending_amount > 0:
                due_lbl = QLabel(f"Due: {format_currency(treatment.pending_amount)}")
                due_lbl.setStyleSheet(
                    "background:#D0534F; color:white; border-radius:10px;"
                    " padding:4px 14px; font-weight:700; font-size:12px;"
                )
                hl.addWidget(due_lbl)
                # Pre-fill the amount
                self._prefill_amount = treatment.pending_amount
            else:
                self._prefill_amount = 0
        except Exception:
            self._prefill_amount = 0

        outer.addWidget(header)

        # ── Form body ──
        body = QWidget()
        body.setStyleSheet("QWidget { background:#FFFFFF; }")
        form = QVBoxLayout(body)
        form.setContentsMargins(28, 24, 28, 20)
        form.setSpacing(18)

        # Amount field
        amt_section = QVBoxLayout()
        amt_section.setSpacing(6)
        amt_label = QLabel("Amount (₹)")
        amt_label.setStyleSheet("font-size:13px; font-weight:600; color:#1E2B32;")
        amt_section.addWidget(amt_label)

        self.amount = QDoubleSpinBox()
        self.amount.setMinimum(1)
        self.amount.setMaximum(1_000_000)
        self.amount.setPrefix("₹ ")
        self.amount.setDecimals(2)
        if self._prefill_amount > 0:
            self.amount.setValue(self._prefill_amount)
        self.amount.setStyleSheet(
            "QDoubleSpinBox { border:1.5px solid #CFDADE; border-radius:8px;"
            " padding:10px 14px; font-size:15px; font-weight:600; background:#F4F7F8; }"
            "QDoubleSpinBox:focus { border:2px solid #1F8A9E; background:white; }"
        )
        amt_section.addWidget(self.amount)
        form.addLayout(amt_section)

        # Payment method
        method_section = QVBoxLayout()
        method_section.setSpacing(6)
        method_label = QLabel("Payment Method")
        method_label.setStyleSheet("font-size:13px; font-weight:600; color:#1E2B32;")
        method_section.addWidget(method_label)

        self.method = QComboBox()
        self.method.addItems(["Cash", "UPI", "Card", "Bank Transfer", "Cheque"])
        self.method.setStyleSheet(
            "QComboBox { border:1.5px solid #CFDADE; border-radius:8px;"
            " padding:10px 14px; font-size:13px; background:#F4F7F8; }"
            "QComboBox:focus { border:2px solid #1F8A9E; background:white; }"
        )
        method_section.addWidget(self.method)
        form.addLayout(method_section)

        # Date
        date_section = QVBoxLayout()
        date_section.setSpacing(6)
        date_label = QLabel("Date")
        date_label.setStyleSheet("font-size:13px; font-weight:600; color:#1E2B32;")
        date_section.addWidget(date_label)

        self.date = QDateEdit()
        self.date.setDate(QDate.currentDate())
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("dd MMM yyyy")
        self.date.setStyleSheet(
            "QDateEdit { border:1.5px solid #CFDADE; border-radius:8px;"
            " padding:10px 14px; font-size:13px; background:#F4F7F8; }"
            "QDateEdit:focus { border:2px solid #1F8A9E; background:white; }"
        )
        date_section.addWidget(self.date)
        form.addLayout(date_section)

        # Notes
        notes_section = QVBoxLayout()
        notes_section.setSpacing(6)
        notes_label = QLabel("Notes (optional)")
        notes_label.setStyleSheet("font-size:13px; font-weight:600; color:#1E2B32;")
        notes_section.addWidget(notes_label)

        self.notes = QTextEdit()
        self.notes.setMaximumHeight(64)
        self.notes.setPlaceholderText("e.g. Cash received at reception")
        self.notes.setStyleSheet(
            "QTextEdit { border:1.5px solid #CFDADE; border-radius:8px;"
            " padding:8px 12px; font-size:13px; background:#F4F7F8; }"
            "QTextEdit:focus { border:2px solid #1F8A9E; background:white; }"
        )
        notes_section.addWidget(self.notes)
        form.addLayout(notes_section)

        # Error / success inline label
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setVisible(False)
        self.status_label.setStyleSheet(
            "padding:8px 14px; border-radius:8px; font-size:13px; font-weight:600;"
        )
        form.addWidget(self.status_label)

        outer.addWidget(body)

        # ── Button bar ──
        btn_bar = QFrame()
        btn_bar.setStyleSheet(
            "QFrame { background:#F8F9FA; border-top:1px solid #DDE5E8; }"
        )
        btn_layout = QHBoxLayout(btn_bar)
        btn_layout.setContentsMargins(28, 14, 28, 14)
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(
            "QPushButton { background:#EEF3F4; color:#1E2B32; border:1px solid #CFDADE;"
            " border-radius:8px; padding:10px 24px; font-weight:600; font-size:13px; }"
            "QPushButton:hover { background:#DDE5E8; }"
        )
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("💾  Save Payment")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(
            "QPushButton { background:#2E9E6B; color:white; border:none;"
            " border-radius:8px; padding:10px 28px; font-weight:700; font-size:13px; }"
            "QPushButton:hover { background:#2A9163; }"
        )
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        outer.addWidget(btn_bar)

    def _on_save(self):
        amount = self.amount.value()
        method = self.method.currentText().lower()
        pay_date = self.date.date().toPyDate()
        notes = self.notes.toPlainText().strip()

        success, message, _ = self.payment_service.add_payment(
            treatment_id=self.treatment_id,
            amount=amount,
            payment_date=pay_date,
            payment_method=method,
            notes=notes if notes else None
        )

        if success:
            # Show inline success toast, then auto-close after 800ms
            self.status_label.setText("✅  Payment recorded successfully!")
            self.status_label.setStyleSheet(
                "background:#E6F5EE; color:#15803D; padding:10px 14px;"
                " border-radius:8px; font-size:13px; font-weight:600;"
                " border:1px solid #86EFAC;"
            )
            self.status_label.setVisible(True)

            from PyQt6.QtCore import QTimer
            QTimer.singleShot(800, self.accept)
        else:
            self.status_label.setText(f"❌  {message}")
            self.status_label.setStyleSheet(
                "background:#FBEBEA; color:#9E3B38; padding:10px 14px;"
                " border-radius:8px; font-size:13px; font-weight:600;"
                " border:1px solid #FCA5A5;"
            )
            self.status_label.setVisible(True)


# ── Prescription Row Widget ───────────────────────────────────────────────────

class _PrescriptionRowWidget(QFrame):
    """One medicine row: Medicine | M-A-E-N spinboxes | Timing | Quantity."""

    TIMING = ["Before Food  (जेवणापूर्वी)",
               "After Food   (जेवणानंतर)",
               "With Food    (जेवणासह)"]

    _spin_style = (
        "QSpinBox { border:1px solid #B9DCE4; border-radius:5px; background:#EEF7F9;"
        " padding:2px; font-size:13px; font-weight:700; }"
    )
    _sep_style = "color:#8A989F; font-size:14px; font-weight:700; background:transparent;"

    def __init__(self, row_num: int, medicine_names: list, on_delete, parent=None):
        super().__init__(parent)
        self._on_delete = on_delete
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("QFrame { background:white; border-bottom:1px solid #E8EEF0; }")
        self.setFixedHeight(48)

        row = QHBoxLayout(self)
        row.setContentsMargins(10, 4, 10, 4)
        row.setSpacing(6)

        # Row number
        self._num_lbl = QLabel(str(row_num))
        self._num_lbl.setFixedWidth(26)
        self._num_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._num_lbl.setStyleSheet("color:#5B6B73; font-size:11px; background:transparent;")
        row.addWidget(self._num_lbl)

        # Medicine name with autocomplete — wider since no dose/freq columns
        self._medicine = QLineEdit()
        self._medicine.setMinimumWidth(220)
        self._medicine.setPlaceholderText("Medicine name…")
        self._medicine.setStyleSheet(
            "QLineEdit { border:1px solid #DDE5E8; border-radius:5px;"
            " padding:5px 10px; font-size:13px; }"
        )
        if medicine_names:
            comp = QCompleter(medicine_names)
            comp.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            comp.setFilterMode(Qt.MatchFlag.MatchContains)
            self._medicine.setCompleter(comp)
        row.addWidget(self._medicine, stretch=1)

        # ── Dosage: M - A - E - N ──
        dosage_lbl = QLabel("Dosage:")
        dosage_lbl.setStyleSheet("color:#5B6B73; font-size:11px; background:transparent;")
        row.addWidget(dosage_lbl)

        self._spins = {}
        for i, key in enumerate(("M", "A", "E", "N")):
            sp = QSpinBox()
            sp.setRange(0, 4)
            sp.setValue(1 if key == "M" else 0)
            sp.setFixedWidth(38)
            sp.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
            sp.setStyleSheet(self._spin_style)
            sp.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._spins[key] = sp
            row.addWidget(sp)
            if i < 3:
                sep = QLabel("-")
                sep.setFixedWidth(12)
                sep.setAlignment(Qt.AlignmentFlag.AlignCenter)
                sep.setStyleSheet(self._sep_style)
                row.addWidget(sep)

        # Timing
        self._timing = QComboBox()
        self._timing.setFixedWidth(165)
        self._timing.addItems(self.TIMING)
        self._timing.setStyleSheet(
            "QComboBox { border:1px solid #DDE5E8; border-radius:5px;"
            " padding:4px 6px; font-size:12px; }"
        )
        row.addWidget(self._timing)

        # Quantity (days)
        qty_lbl = QLabel("Qty:")
        qty_lbl.setStyleSheet("color:#5B6B73; font-size:11px; background:transparent;")
        row.addWidget(qty_lbl)

        self._days = QSpinBox()
        self._days.setRange(1, 365)
        self._days.setValue(5)
        self._days.setFixedWidth(56)
        self._days.setStyleSheet(
            "QSpinBox { border:1px solid #DDE5E8; border-radius:5px;"
            " padding:3px; font-size:12px; }"
        )
        row.addWidget(self._days)

        # Delete
        del_btn = QPushButton("✕")
        del_btn.setFixedSize(28, 28)
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet(
            "QPushButton { background:#FBEBEA; color:#9E3B38; border:none;"
            " border-radius:6px; font-weight:700; }"
            "QPushButton:hover { background:#F8DEDD; }"
        )
        del_btn.clicked.connect(lambda: self._on_delete(self))
        row.addWidget(del_btn)

    def set_num(self, n: int):
        self._num_lbl.setText(str(n))

    def get_data(self) -> dict:
        return {
            "medicine": self._medicine.text().strip(),
            "M": self._spins["M"].value(),
            "A": self._spins["A"].value(),
            "E": self._spins["E"].value(),
            "N": self._spins["N"].value(),
            "timing": self._timing.currentText(),
            "days":   self._days.value(),
        }
