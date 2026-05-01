"""Due Payments page — dedicated view of all outstanding patient balances."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QDialog, QScrollArea,
    QSizePolicy, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QBrush

from ...services.treatment_service import TreatmentService
from .payment_list import RecordPaymentDialog


class DuePaymentsWidget(QWidget):
    """Full-featured due payments tracking page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.treatment_service = TreatmentService()
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
            " stop:0 #7A2E0F, stop:0.6 #B8450D, stop:1 #D4680A);"
            " border-radius: 14px; }"
        )
        banner.setFixedHeight(110)
        banner_layout = QHBoxLayout(banner)
        banner_layout.setContentsMargins(28, 0, 28, 0)

        banner_text = QVBoxLayout()
        b_title = QLabel("Due Payments")
        b_title.setStyleSheet(
            "color:white; font-size:24px; font-weight:700; background:transparent;"
        )
        b_subtitle = QLabel("Track outstanding patient balances")
        b_subtitle.setStyleSheet(
            "color:#E8C4A8; font-size:13px; background:transparent;"
        )
        banner_text.addStretch()
        banner_text.addWidget(b_title)
        banner_text.addWidget(b_subtitle)
        banner_text.addStretch()
        banner_layout.addLayout(banner_text)
        banner_layout.addStretch()

        self.total_badge = QLabel("0 due")
        self.total_badge.setStyleSheet(
            "color:white; font-size:13px; font-weight:600;"
            " background:rgba(255,255,255,0.18); border-radius:14px;"
            " padding:6px 18px;"
        )
        banner_layout.addWidget(self.total_badge)

        layout.addWidget(banner)

        # ── Summary cards ──
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)

        self.card_outstanding = self._make_summary_card(
            "Total Outstanding", "Rs.0", "#FF9500", "Due"
        )
        self.card_patients = self._make_summary_card(
            "Patients with Dues", "0", "#007AFF", "Patients"
        )
        self.card_treatments = self._make_summary_card(
            "Treatments with Dues", "0", "#FF3B30", "Pending"
        )
        cards_row.addWidget(self.card_outstanding)
        cards_row.addWidget(self.card_patients)
        cards_row.addWidget(self.card_treatments)
        layout.addLayout(cards_row)

        # ── Search row ──
        filter_row = QHBoxLayout()
        filter_row.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by patient name or treatment…")
        self.search_input.setFixedHeight(40)
        self.search_input.textChanged.connect(self._apply_filter)
        filter_row.addWidget(self.search_input, 1)

        layout.addLayout(filter_row)

        # ── Due payments table ──
        table_frame = QFrame()
        table_frame.setObjectName("card")
        table_frame.setStyleSheet(
            "QFrame#card { background:#FFFFFF; border:1px solid #E5E5EA;"
            " border-radius:12px; padding:0px; }"
        )
        tbl_layout = QVBoxLayout(table_frame)
        tbl_layout.setContentsMargins(0, 0, 0, 0)
        tbl_layout.setSpacing(0)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Patient", "Treatment", "Total Cost", "Paid", "Due Amount", ""]
        )
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            5, QHeaderView.ResizeMode.Fixed
        )
        self.table.setColumnWidth(5, 120)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(50)
        self.table.setFrameShape(QFrame.Shape.NoFrame)

        # Style the header
        self.table.horizontalHeader().setStyleSheet(
            "QHeaderView::section {"
            "  background:#F8F8FA; color:#6B7280; font-weight:600;"
            "  font-size:11px; border:none; padding:10px 12px;"
            "  border-bottom:2px solid #E5E5EA;"
            "}"
        )

        tbl_layout.addWidget(self.table)
        layout.addWidget(table_frame)

        # ── Empty state ──
        self.empty_lbl = QLabel("No outstanding payments. All treatments are fully paid!")
        self.empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_lbl.setStyleSheet(
            "color:#86868B; font-size:15px; padding:40px;"
        )
        self.empty_lbl.hide()
        layout.addWidget(self.empty_lbl)

        layout.addStretch()

        self.refresh_data()

    # ── Summary card factory ──────────────────────────────────────────────────

    def _make_summary_card(
        self, label: str, value: str, accent: str, icon: str
    ) -> QFrame:
        card = QFrame()
        card.setObjectName("metric_card")
        card.setStyleSheet(
            f"QFrame#metric_card {{ background:#FFFFFF; border:1px solid #E5E5EA;"
            f" border-left: 4px solid {accent}; border-radius:10px; }}"
        )
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        card.setFixedHeight(100)

        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 14, 20, 14)
        cl.setSpacing(6)

        top_row = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(
            f"font-size:10px; font-weight:bold; color:#fff;"
            f" background:{accent}; border-radius:9px; padding:2px 8px;"
        )
        icon_lbl.setMaximumWidth(70)
        top_row.addWidget(icon_lbl)
        top_row.addStretch()
        cl.addLayout(top_row)

        val_lbl = QLabel(value)
        val_lbl.setObjectName("metric_value")
        val_lbl.setStyleSheet(
            f"font-size:22px; font-weight:700; color:{accent}; background:transparent;"
            f" font-family: 'Noto Sans', 'DejaVu Sans', 'Segoe UI', sans-serif;"
        )
        cl.addWidget(val_lbl)

        lbl_lbl = QLabel(label)
        lbl_lbl.setObjectName("metric_label")
        lbl_lbl.setStyleSheet(
            "font-size:11px; color:#86868B; background:transparent;"
            " font-family: 'Ubuntu', 'Segoe UI', sans-serif;"
        )
        cl.addWidget(lbl_lbl)

        card._value_label = val_lbl
        return card

    # ── Data loading ──────────────────────────────────────────────────────────

    def refresh_data(self):
        self._load_data()
        self._update_summary()
        self._apply_filter()

    def _load_data(self):
        self._all_rows = []
        try:
            pending = self.treatment_service.get_pending_with_patient_names()
            for item in pending:
                t = item['treatment']
                self._all_rows.append({
                    'patient_name': item['patient_name'],
                    'patient_mobile': item['patient_mobile'],
                    'treatment_name': t.treatment_type_name or '—',
                    'total_cost': t.total_cost,
                    'amount_paid': t.amount_paid,
                    'due_amount': t.pending_amount,
                    'treatment_id': t.id,
                    'patient_id': item['patient_id'],
                })
        except Exception:
            pass

        # Sort by due amount descending (highest dues first)
        self._all_rows.sort(key=lambda r: r['due_amount'], reverse=True)

    def _update_summary(self):
        total_outstanding = sum(r['due_amount'] for r in self._all_rows)
        unique_patients = len({r['patient_id'] for r in self._all_rows})
        num_treatments = len(self._all_rows)

        self.card_outstanding._value_label.setText(f"Rs.{total_outstanding:,.0f}")
        self.card_patients._value_label.setText(str(unique_patients))
        self.card_treatments._value_label.setText(str(num_treatments))
        self.total_badge.setText(
            f"{num_treatments} due" if num_treatments else "All clear"
        )

    # ── Filtering ─────────────────────────────────────────────────────────────

    def _apply_filter(self):
        search_text = self.search_input.text().strip().lower()

        filtered = []
        for row in self._all_rows:
            if search_text:
                haystack = (
                    row['patient_name'].lower()
                    + row['treatment_name'].lower()
                )
                if search_text not in haystack:
                    continue
            filtered.append(row)

        self._populate_table(filtered)

    def _populate_table(self, rows: list[dict]):
        self.table.setRowCount(0)

        if not rows:
            self.table.hide()
            self.empty_lbl.show()
            return

        self.table.show()
        self.empty_lbl.hide()

        for row_data in rows:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)

            # Patient name (bold, dark blue)
            name_item = QTableWidgetItem(row_data['patient_name'])
            name_item.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            name_item.setForeground(QBrush(QColor("#0F2942")))
            self.table.setItem(row_idx, 0, name_item)

            # Treatment
            treat_item = QTableWidgetItem(row_data['treatment_name'])
            treat_item.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row_idx, 1, treat_item)

            # Total cost (right-aligned)
            cost_item = QTableWidgetItem(f"Rs.{row_data['total_cost']:,.0f}")
            cost_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            cost_item.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row_idx, 2, cost_item)

            # Paid (right-aligned, green)
            paid_item = QTableWidgetItem(f"Rs.{row_data['amount_paid']:,.0f}")
            paid_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            paid_item.setFont(QFont("Segoe UI", 11))
            paid_item.setForeground(QBrush(QColor("#34C759")))
            self.table.setItem(row_idx, 3, paid_item)

            # Due amount (right-aligned, bold, orange)
            due_item = QTableWidgetItem(f"Rs.{row_data['due_amount']:,.0f}")
            due_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            due_item.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            due_item.setForeground(QBrush(QColor("#FF9500")))
            self.table.setItem(row_idx, 4, due_item)

            # Pay Now button
            pay_btn = QPushButton("Pay Now")
            pay_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            pay_btn.setFixedSize(100, 34)
            pay_btn.setStyleSheet(
                "QPushButton {"
                "  background:#007AFF; color:white; border:none;"
                "  border-radius:8px; font-weight:600; font-size:12px;"
                "}"
                "QPushButton:hover { background:#0056D6; }"
                "QPushButton:pressed { background:#004BB5; }"
            )
            pay_btn.clicked.connect(
                lambda _, tid=row_data['treatment_id']: self._on_pay_now(tid)
            )
            # Center the button in the cell
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(8, 4, 8, 4)
            btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn_layout.addWidget(pay_btn)
            self.table.setCellWidget(row_idx, 5, btn_container)

    # ── Pay Now action ────────────────────────────────────────────────────────

    def _on_pay_now(self, treatment_id: int):
        dialog = RecordPaymentDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
