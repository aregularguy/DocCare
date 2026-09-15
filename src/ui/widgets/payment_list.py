"""Payments page — record, view, and summarise all payments."""
from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QDialog, QFormLayout, QComboBox,
    QDoubleSpinBox, QDateEdit, QMessageBox, QScrollArea,
    QCompleter, QSizePolicy, QAbstractItemView
)
from PyQt6.QtCore import Qt, QDate, QStringListModel
from PyQt6.QtGui import QFont, QColor, QBrush

from ...services.patient_service import PatientService
from ...services.treatment_service import TreatmentService
from ...services.payment_service import PaymentService
from ...utils.formatters import format_currency


METHOD_COLORS = {
    'cash':   ('#E6F5EE', '#2E9E6B'),
    'card':   ('#E3F3F6', '#1F8A9E'),
    'upi':    ('#EEEFF8', '#6E72B8'),
    'cheque': ('#FBF1E1', '#C98A2E'),
    'other':  ('#EEF3F4', '#5B6B73'),
}


def _method_badge(method: str) -> QLabel:
    key = (method or 'other').lower()
    bg, fg = METHOD_COLORS.get(key, METHOD_COLORS['other'])
    lbl = QLabel(method.upper() if method else 'OTHER')
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setMinimumHeight(24)
    lbl.setStyleSheet(
        f"background:{bg}; color:{fg}; border-radius:12px;"
        f" padding:3px 12px; font-weight:700; font-size:11px;"
    )
    return lbl


class RecordPaymentDialog(QDialog):
    """Dialog to record a payment against a treatment."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Record Payment")
        self.setMinimumWidth(480)
        self.setModal(True)

        self.patient_service = PatientService()
        self.treatment_service = TreatmentService()
        self.payment_service = PaymentService()

        self._patients = []
        self._treatments = []
        self._selected_patient = None
        self._selected_treatment = None

        self._build_ui()
        self._load_patients()

    # ── Build UI ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Title bar
        title_bar = QFrame()
        title_bar.setStyleSheet(
            "QFrame { background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            " stop:0 #1F4E5A, stop:0.6 #2A6674, stop:1 #3A8C99);"
            " border-radius: 0px; }"
        )
        title_bar.setFixedHeight(60)
        tb_layout = QHBoxLayout(title_bar)
        tb_layout.setContentsMargins(24, 0, 24, 0)
        icon_lbl = QLabel("💳")
        icon_lbl.setStyleSheet("color:white; font-size:22px; background:transparent;")
        tb_layout.addWidget(icon_lbl)
        title_lbl = QLabel("Record Payment")
        title_lbl.setStyleSheet(
            "color:white; font-size:16px; font-weight:700; background:transparent;"
        )
        tb_layout.addWidget(title_lbl)
        tb_layout.addStretch()
        outer.addWidget(title_bar)

        # Form body
        body = QWidget()
        body.setStyleSheet("QWidget { background:#FFFFFF; }")
        form_layout = QFormLayout(body)
        form_layout.setContentsMargins(28, 24, 28, 24)
        form_layout.setSpacing(16)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Patient search
        self.patient_search = QLineEdit()
        self.patient_search.setPlaceholderText("Type patient name…")
        self._completer_model = QStringListModel()
        completer = QCompleter()
        completer.setModel(self._completer_model)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.activated.connect(self._on_patient_selected)
        self.patient_search.setCompleter(completer)
        self.patient_search.textChanged.connect(self._filter_patients)
        form_layout.addRow("Patient *:", self.patient_search)

        self.patient_info_lbl = QLabel("")
        self.patient_info_lbl.setStyleSheet(
            "color:#1F8A9E; font-size:12px; background:transparent;"
        )
        form_layout.addRow("", self.patient_info_lbl)

        # Treatment dropdown
        self.treatment_combo = QComboBox()
        self.treatment_combo.setPlaceholderText("Select treatment…")
        self.treatment_combo.setEnabled(False)
        self.treatment_combo.currentIndexChanged.connect(self._on_treatment_changed)
        form_layout.addRow("Treatment *:", self.treatment_combo)

        # Amount
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setPrefix("Rs. ")
        self.amount_spin.setRange(0.01, 9_999_999.0)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setValue(0.01)
        self.amount_spin.setEnabled(False)
        form_layout.addRow("Amount *:", self.amount_spin)

        self.pending_lbl = QLabel("")
        self.pending_lbl.setStyleSheet(
            "color:#C98A2E; font-size:12px; background:transparent;"
        )
        form_layout.addRow("", self.pending_lbl)

        # Method
        self.method_combo = QComboBox()
        for m in ["Cash", "Card", "UPI", "Cheque", "Other"]:
            self.method_combo.addItem(m, m.lower())
        form_layout.addRow("Method *:", self.method_combo)

        # Date
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd MMM yyyy")
        form_layout.addRow("Date *:", self.date_edit)

        # Notes
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Optional notes…")
        form_layout.addRow("Notes:", self.notes_input)

        # Error label
        self.error_lbl = QLabel("")
        self.error_lbl.setObjectName("error_label")
        self.error_lbl.setWordWrap(True)
        form_layout.addRow("", self.error_lbl)

        outer.addWidget(body)

        # Buttons
        btn_bar = QFrame()
        btn_bar.setStyleSheet(
            "QFrame { background:#EEF3F4; border-top:1px solid #DDE5E8; }"
        )
        btn_layout = QHBoxLayout(btn_bar)
        btn_layout.setContentsMargins(28, 14, 28, 14)
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary_button")
        cancel_btn.setFixedWidth(100)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        self.save_btn = QPushButton("💾  Save Payment")
        self.save_btn.setObjectName("primary_button")
        self.save_btn.setFixedWidth(160)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(self.save_btn)

        outer.addWidget(btn_bar)

    # ── Data helpers ──────────────────────────────────────────────────────────

    def _load_patients(self):
        self._patients = self.patient_service.get_all_patients()
        names = [p.name for p in self._patients]
        self._completer_model.setStringList(names)

    def _filter_patients(self, text: str):
        if not text.strip():
            self._selected_patient = None
            self.patient_info_lbl.setText("")
            self.treatment_combo.setEnabled(False)
            self.treatment_combo.clear()
            self.amount_spin.setEnabled(False)
            return

    def _on_patient_selected(self, name: str):
        for p in self._patients:
            if p.name == name:
                self._selected_patient = p
                self.patient_search.setText(p.name)
                self.patient_info_lbl.setText(
                    f"📞 {p.mobile or '—'}  ·  ID #{p.id}"
                )
                self._load_treatments(p.id)
                return

    def _load_treatments(self, patient_id: int):
        self._treatments = self.treatment_service.get_patient_treatments(patient_id)
        self.treatment_combo.clear()
        self.treatment_combo.setEnabled(False)
        self.amount_spin.setEnabled(False)
        self.pending_lbl.setText("")

        payable = [t for t in self._treatments if t.pending_amount > 0]
        if not payable:
            self.treatment_combo.addItem("No treatments with pending amount", -1)
            return

        self.treatment_combo.setEnabled(True)
        self.treatment_combo.addItem("— select treatment —", -1)
        for t in payable:
            label = f"{t.treatment_type_name}  ({format_currency(t.pending_amount)} pending)"
            self.treatment_combo.addItem(label, t.id)

    def _on_treatment_changed(self, idx: int):
        t_id = self.treatment_combo.currentData()
        if not t_id or t_id == -1:
            self.amount_spin.setEnabled(False)
            self.pending_lbl.setText("")
            return

        for t in self._treatments:
            if t.id == t_id:
                self._selected_treatment = t
                self.amount_spin.setMaximum(t.pending_amount)
                self.amount_spin.setValue(t.pending_amount)
                self.amount_spin.setEnabled(True)
                self.pending_lbl.setText(
                    f"Pending: {format_currency(t.pending_amount)}  ·  Total cost: {format_currency(t.total_cost)}"
                )
                return

    # ── Save ──────────────────────────────────────────────────────────────────

    def _on_save(self):
        self.error_lbl.setText("")

        if not self._selected_patient:
            self.error_lbl.setText("Please select a patient.")
            return

        t_id = self.treatment_combo.currentData()
        if not t_id or t_id == -1:
            self.error_lbl.setText("Please select a treatment.")
            return

        amount = self.amount_spin.value()
        if amount <= 0:
            self.error_lbl.setText("Amount must be greater than zero.")
            return

        q_date = self.date_edit.date()
        pay_date = date(q_date.year(), q_date.month(), q_date.day())
        method = self.method_combo.currentData()
        notes = self.notes_input.text().strip() or None

        ok, msg, _ = self.payment_service.add_payment(
            treatment_id=t_id,
            amount=amount,
            payment_date=pay_date,
            payment_method=method,
            notes=notes
        )
        if ok:
            self.accept()
        else:
            self.error_lbl.setText(f"Error: {msg}")


# ── Main page widget ──────────────────────────────────────────────────────────

class PaymentListWidget(QWidget):
    """Full-featured payments page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.patient_service = PatientService()
        self.treatment_service = TreatmentService()
        self.payment_service = PaymentService()
        self._all_rows: list[dict] = []
        self.init_ui()

    # ── UI construction ───────────────────────────────────────────────────────

    def init_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(scroll)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 28, 32, 32)
        layout.setSpacing(20)
        scroll.setWidget(container)

        # ── Hero banner ──
        banner = QFrame()
        banner.setStyleSheet(
            "QFrame { background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            " stop:0 #1F4E5A, stop:0.6 #2A6674, stop:1 #3A8C99);"
            " border-radius: 14px; }"
        )
        banner.setFixedHeight(110)
        banner_layout = QHBoxLayout(banner)
        banner_layout.setContentsMargins(28, 0, 28, 0)

        banner_text = QVBoxLayout()
        b_title = QLabel("💳  Payments")
        b_title.setStyleSheet(
            "color:white; font-size:24px; font-weight:700; background:transparent;"
        )
        b_subtitle = QLabel("Track and manage all patient payment transactions")
        b_subtitle.setStyleSheet(
            "color:#A9CBD2; font-size:13px; background:transparent;"
        )
        banner_text.addStretch()
        banner_text.addWidget(b_title)
        banner_text.addWidget(b_subtitle)
        banner_text.addStretch()
        banner_layout.addLayout(banner_text)
        banner_layout.addStretch()

        self.record_btn = QPushButton("➕  Record Payment")
        self.record_btn.setObjectName("primary_button")
        self.record_btn.setFixedSize(180, 42)
        self.record_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.record_btn.clicked.connect(self._open_record_dialog)
        banner_layout.addWidget(self.record_btn)

        layout.addWidget(banner)

        # ── Summary cards ──
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)

        self.card_today = self._make_summary_card(
            "Total Collected Today", format_currency(0), "#2E9E6B", "💰"
        )
        self.card_month = self._make_summary_card(
            "Total Collected This Month", format_currency(0), "#1F8A9E", "📅"
        )
        self.card_pending = self._make_summary_card(
            "Total Outstanding", format_currency(0), "#C98A2E", "⏳"
        )
        cards_row.addWidget(self.card_today)
        cards_row.addWidget(self.card_month)
        cards_row.addWidget(self.card_pending)
        layout.addLayout(cards_row)

        # ── Filters row ──
        filter_row = QHBoxLayout()
        filter_row.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search by patient or treatment…")
        self.search_input.setFixedHeight(40)
        self.search_input.textChanged.connect(self._apply_filter)
        filter_row.addWidget(self.search_input, 1)

        self.method_filter = QComboBox()
        self.method_filter.setFixedHeight(40)
        self.method_filter.addItem("All Methods", "")
        for m in ["Cash", "Card", "UPI", "Cheque", "Other"]:
            self.method_filter.addItem(m, m.lower())
        self.method_filter.currentIndexChanged.connect(self._apply_filter)
        filter_row.addWidget(self.method_filter)

        layout.addLayout(filter_row)

        # ── Payments table ──
        table_frame = QFrame()
        table_frame.setObjectName("card")
        table_frame.setStyleSheet(
            "QFrame#card { background:#FFFFFF; border:1px solid #DDE5E8;"
            " border-radius:12px; padding:0px; }"
        )
        tbl_layout = QVBoxLayout(table_frame)
        tbl_layout.setContentsMargins(0, 0, 0, 0)
        tbl_layout.setSpacing(0)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Patient", "Treatment", "Amount", "Method", "Date", "Notes"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        # ResizeToContents ignores cell widgets, which clipped the method badge
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 130)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setColumnWidth(0, 240)
        self.table.setColumnWidth(1, 260)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(46)
        self.table.setFrameShape(QFrame.Shape.NoFrame)
        tbl_layout.addWidget(self.table)

        layout.addWidget(table_frame)

        # ── Empty state label ──
        self.empty_lbl = QLabel("No payments recorded yet.")
        self.empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_lbl.setStyleSheet(
            "color:#5B6B73; font-size:15px; padding:40px;"
        )
        self.empty_lbl.hide()
        layout.addWidget(self.empty_lbl)

        layout.addStretch()

        # Load data immediately on first open
        self._load_summary()
        self._load_table()

    # ── Summary card factory ──────────────────────────────────────────────────

    def _make_summary_card(
        self, label: str, value: str, accent: str, icon: str
    ) -> QFrame:
        card = QFrame()
        card.setObjectName("metric_card")
        card.setStyleSheet(
            f"QFrame#metric_card {{ background:#FFFFFF; border:1px solid #DDE5E8;"
            f" border-left: 4px solid {accent}; border-radius:10px; padding:0px; }}"
        )
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        card.setMinimumHeight(100)

        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 14, 20, 14)
        cl.setSpacing(6)

        top_row = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(
            f"font-size:22px; background:transparent; color:{accent};"
        )
        top_row.addWidget(icon_lbl)
        top_row.addStretch()
        cl.addLayout(top_row)

        val_lbl = QLabel(value)
        val_lbl.setObjectName("metric_value")
        # Use Noto Sans / DejaVu Sans for full ₹ Unicode glyph support at large sizes
        val_lbl.setStyleSheet(
            f"font-size:20pt; font-weight:700; color:{accent}; background:transparent;"
            f" font-family: 'Noto Sans', 'DejaVu Sans', 'Segoe UI', sans-serif;"
        )
        cl.addWidget(val_lbl)

        lbl_lbl = QLabel(label)
        lbl_lbl.setObjectName("metric_label")
        lbl_lbl.setStyleSheet(
            "font-size:11px; color:#5B6B73; background:transparent;"
            " font-family: 'Ubuntu', 'Segoe UI', sans-serif;"
        )
        cl.addWidget(lbl_lbl)

        # stash references for later updates
        card._value_label = val_lbl
        return card

    # ── Data loading ──────────────────────────────────────────────────────────

    def refresh_data(self):
        """Load / reload all payment data and update the UI."""
        self._load_summary()
        self._load_table()

    def _load_summary(self):
        try:
            today = date.today()
            month_start = today.replace(day=1)

            total_today = self.payment_service.get_total_by_date_range(today, today) or 0.0
            total_month = self.payment_service.get_total_by_date_range(month_start, today) or 0.0

            pending_treatments = self.treatment_service.get_pending_payments()
            total_outstanding = sum(
                t.pending_amount for t in pending_treatments if t.pending_amount > 0
            )

            self.card_today._value_label.setText(format_currency(total_today))
            self.card_month._value_label.setText(format_currency(total_month))
            self.card_pending._value_label.setText(format_currency(total_outstanding))
        except Exception as e:
            self.card_today._value_label.setText(format_currency(0))
            self.card_month._value_label.setText(format_currency(0))
            self.card_pending._value_label.setText(format_currency(0))

    def _load_table(self):
        self._all_rows = []

        patients = self.patient_service.get_all_patients()
        for patient in patients:
            treatments = self.treatment_service.get_patient_treatments(patient.id)
            for treatment in treatments:
                payments = self.payment_service.get_treatment_payments(treatment.id)
                for payment in payments:
                    self._all_rows.append({
                        'patient_name': patient.name,
                        'treatment_name': treatment.treatment_type_name or '—',
                        'amount': payment.amount,
                        'method': payment.payment_method or 'other',
                        'date': payment.payment_date,
                        'notes': payment.notes or '',
                    })

        # Sort newest first
        self._all_rows.sort(
            key=lambda r: r['date'] or date.min, reverse=True
        )
        self._apply_filter()

    # ── Filtering ─────────────────────────────────────────────────────────────

    def _apply_filter(self):
        search_text = self.search_input.text().strip().lower()
        method_filter = self.method_filter.currentData()

        filtered = []
        for row in self._all_rows:
            if search_text:
                haystack = (
                    row['patient_name'].lower()
                    + row['treatment_name'].lower()
                    + row['notes'].lower()
                )
                if search_text not in haystack:
                    continue
            if method_filter:
                if row['method'].lower() != method_filter:
                    continue
            filtered.append(row)

        self._populate_table(filtered)

    def _populate_table(self, rows: list[dict]):
        self.table.setRowCount(0)

        if not rows:
            self.table.hide()
            self.empty_lbl.show()
            return

        self.empty_lbl.hide()
        self.table.show()
        self.table.setRowCount(len(rows))

        for r_idx, row in enumerate(rows):
            # Patient name — bold
            patient_item = QTableWidgetItem(row['patient_name'])
            patient_item.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
            self.table.setItem(r_idx, 0, patient_item)

            # Treatment name
            self.table.setItem(
                r_idx, 1, QTableWidgetItem(row['treatment_name'])
            )

            # Amount
            amt_item = QTableWidgetItem(format_currency(row['amount']))
            amt_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            amt_item.setForeground(QBrush(QColor("#2E9E6B")))
            f = amt_item.font()
            f.setBold(True)
            amt_item.setFont(f)
            self.table.setItem(r_idx, 2, amt_item)

            # Method — use a centered widget with the badge
            method_key = (row['method'] or 'other').lower()
            badge = _method_badge(method_key)
            badge_container = QWidget()
            badge_container.setStyleSheet("background:transparent;")
            bc_layout = QHBoxLayout(badge_container)
            bc_layout.setContentsMargins(8, 4, 8, 4)
            bc_layout.addStretch()
            bc_layout.addWidget(badge)
            bc_layout.addStretch()
            self.table.setCellWidget(r_idx, 3, badge_container)

            # Date
            date_str = (
                row['date'].strftime('%d %b %Y')
                if row['date'] else '—'
            )
            date_item = QTableWidgetItem(date_str)
            date_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
            )
            self.table.setItem(r_idx, 4, date_item)

            # Notes
            self.table.setItem(r_idx, 5, QTableWidgetItem(row['notes']))

    # ── Slot: open record dialog ──────────────────────────────────────────────

    def _open_record_dialog(self):
        dlg = RecordPaymentDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
            QMessageBox.information(
                self, "Payment Recorded", "Payment has been saved successfully."
            )
